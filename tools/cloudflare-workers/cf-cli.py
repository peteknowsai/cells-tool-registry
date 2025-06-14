#!/usr/bin/env python3
"""
Cloudflare Workers CLI - Manage Workers, Durable Objects, Routes, and KV Storage
"""

import argparse
import json
import os
import sys
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
from datetime import datetime

# Configuration
CONFIG_DIR = Path.home() / ".cf-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
BASE_URL = "https://api.cloudflare.com/client/v4"

class CloudflareAPI:
    """Cloudflare API client"""
    
    def __init__(self):
        self.config = self.load_config()
        self.api_token = self.config.get('api_token') or os.environ.get('CLOUDFLARE_API_TOKEN')
        self.account_id = self.config.get('account_id') or os.environ.get('CLOUDFLARE_ACCOUNT_ID')
        
        if not self.api_token or not self.account_id:
            print("Error: Missing Cloudflare credentials")
            print("Run 'cf-cli auth init' or set environment variables:")
            print("  export CLOUDFLARE_API_TOKEN=your-token")
            print("  export CLOUDFLARE_ACCOUNT_ID=your-account-id")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: dict):
        """Save configuration to file"""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make API request with error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        # Handle headers
        headers = self.headers.copy()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        if 'files' in kwargs:
            headers.pop('Content-Type', None)
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        try:
            data = response.json()
        except:
            data = {"success": False, "errors": [{"message": response.text}]}
        
        if not data.get('success', False):
            errors = data.get('errors', [])
            error_msg = errors[0]['message'] if errors else 'Unknown error'
            # Special handling for authentication errors
            if 'Authentication error' in error_msg:
                error_msg += f"\nEndpoint: {endpoint}\nStatus: {response.status_code}"
            raise Exception(f"API Error: {error_msg}")
        
        return data.get('result', data)
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Get zone ID from domain name"""
        # Extract root domain from pattern like *.cells.fidelity.com
        if '*' in domain:
            parts = domain.replace('*', '').strip('.').split('.')
            root_domain = '.'.join(parts[-2:]) if len(parts) >= 2 else domain
        else:
            parts = domain.split('.')
            root_domain = '.'.join(parts[-2:]) if len(parts) >= 2 else domain
        
        result = self.request('GET', f'/zones?name={root_domain}')
        zones = result if isinstance(result, list) else []
        
        if not zones:
            # Try parent domain
            parts = root_domain.split('.')
            if len(parts) > 2:
                parent_domain = '.'.join(parts[-2:])
                result = self.request('GET', f'/zones?name={parent_domain}')
                zones = result if isinstance(result, list) else []
        
        return zones[0]['id'] if zones else None

class WorkerManager:
    """Manage Cloudflare Workers"""
    
    def __init__(self, api: CloudflareAPI):
        self.api = api
    
    def detect_durable_objects(self, code: str) -> List[str]:
        """Parse JavaScript to find Durable Object classes"""
        # Multiple patterns to catch different DO class styles
        patterns = [
            r'export\s+class\s+(\w+)\s+extends\s+DurableObject',
            r'export\s+class\s+(\w+)\s*{[^}]*\basync\s+fetch\s*\(',
            r'class\s+(\w+)\s+extends\s+DurableObject',
        ]
        
        classes = []
        for pattern in patterns:
            classes.extend(re.findall(pattern, code, re.MULTILINE | re.DOTALL))
        
        return list(set(classes))  # Remove duplicates
    
    def create_worker(self, name: str, path: str) -> dict:
        """Create and deploy a worker from local files"""
        worker_path = Path(path)
        
        # Find main file
        main_file = None
        for filename in ['index.js', 'worker.js', f'{name}.js', 'index.ts', 'worker.ts']:
            if (worker_path / filename).exists():
                main_file = filename
                break
        
        if not main_file:
            raise Exception(f"No worker file found in {path}")
        
        # Read worker code
        with open(worker_path / main_file, 'r') as f:
            worker_code = f.read()
        
        # Detect Durable Objects
        durable_objects = self.detect_durable_objects(worker_code)
        
        # Build metadata
        metadata = {
            "main_module": main_file,
            "compatibility_date": "2024-01-01"
        }
        
        # Add DO classes info if detected
        if durable_objects:
            print(f"Detected Durable Object classes: {', '.join(durable_objects)}")
            print("Note: Run 'cf-cli create durable-object' to bind them after deployment")
        
        # Check for wrangler.toml for additional config
        wrangler_path = worker_path / 'wrangler.toml'
        if wrangler_path.exists():
            print(f"Note: Found wrangler.toml - some settings may need manual configuration")
        
        # All workers now use multipart format
        # Metadata is required and must specify if using modules
        is_module = 'export default' in worker_code or 'export {' in worker_code
        
        if is_module:
            # ES modules need usage_model specified
            metadata["usage_model"] = "bundled"
        
        # Prepare multipart upload
        files = {
            'metadata': (None, json.dumps(metadata), 'application/json'),
            main_file: (main_file, worker_code, 'application/javascript')
        }
        
        # Upload worker
        print(f"Deploying worker '{name}' from {path}")
        result = self.api.request(
            'PUT',
            f'/accounts/{self.api.account_id}/workers/scripts/{name}',
            files=files
        )
        
        print(f"✓ Worker '{name}' deployed successfully")
        if durable_objects:
            print(f"✓ Durable Objects ready: {', '.join(durable_objects)}")
        
        return result
    
    def deploy(self, name: str) -> dict:
        """Deploy or update existing worker"""
        # Look for worker in common locations
        paths = [
            f"./workers/{name}",
            f"./{name}",
            "./src",
            "."
        ]
        
        for path in paths:
            if Path(path).exists() and any(
                (Path(path) / f).exists() 
                for f in ['index.js', 'worker.js', f'{name}.js', 'index.ts', 'worker.ts']
            ):
                return self.create_worker(name, path)
        
        raise Exception(f"Worker files not found for '{name}'. Searched in: {', '.join(paths)}")
    
    def list_workers(self) -> List[dict]:
        """List all workers"""
        result = self.api.request('GET', f'/accounts/{self.api.account_id}/workers/scripts')
        return result if isinstance(result, list) else []
    
    def delete_worker(self, name: str) -> dict:
        """Delete a worker"""
        result = self.api.request('DELETE', f'/accounts/{self.api.account_id}/workers/scripts/{name}')
        print(f"✓ Worker '{name}' deleted successfully")
        return result
    
    def get_worker_metadata(self, name: str) -> dict:
        """Get worker metadata including bindings"""
        # First get the script details
        result = self.api.request('GET', f'/accounts/{self.api.account_id}/workers/scripts/{name}')
        return result

class DurableObjectManager:
    """Manage Durable Objects"""
    
    def __init__(self, api: CloudflareAPI, worker_manager: WorkerManager):
        self.api = api
        self.worker_manager = worker_manager
    
    def create_durable_object(self, worker_name: str, binding_name: str, class_name: str) -> dict:
        """Add Durable Object binding to existing worker"""
        # Get current worker code and metadata
        print(f"Adding Durable Object binding '{binding_name}' for class '{class_name}'")
        
        # Get worker content
        response = requests.get(
            f"{BASE_URL}/accounts/{self.api.account_id}/workers/scripts/{worker_name}/content",
            headers=self.api.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Worker '{worker_name}' not found")
        
        worker_code = response.text
        
        # Validate class exists
        detected_classes = self.worker_manager.detect_durable_objects(worker_code)
        if class_name not in detected_classes:
            raise Exception(
                f"Class '{class_name}' not found in worker '{worker_name}'. "
                f"Available classes: {', '.join(detected_classes) if detected_classes else 'None'}"
            )
        
        # Build new metadata with DO binding
        do_binding = {
            "type": "durable_object_namespace",
            "name": binding_name,
            "class_name": class_name,
            "script_name": worker_name
        }
        
        # Get existing metadata (simplified for now)
        metadata = {
            "main_module": "index.js",
            "compatibility_date": "2024-01-01",
            "bindings": [do_binding],
            "migrations": [{
                "tag": "v1",
                "new_sqlite_classes": [class_name]
            }]
        }
        
        # Redeploy with new metadata
        files = {
            'metadata': (None, json.dumps(metadata), 'application/json'),
            'index.js': ('index.js', worker_code, 'application/javascript')
        }
        
        result = self.api.request(
            'PUT',
            f'/accounts/{self.api.account_id}/workers/scripts/{worker_name}',
            files=files
        )
        
        print(f"✓ Durable Object binding '{binding_name}' created for class '{class_name}'")
        return result

class RouteManager:
    """Manage Worker routes"""
    
    def __init__(self, api: CloudflareAPI):
        self.api = api
    
    def add_route(self, pattern: str, worker_name: str) -> dict:
        """Add route pattern to worker"""
        # Extract domain from pattern
        domain = pattern.replace('*', '').strip('.').strip('/')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # Get zone ID
        zone_id = self.api.get_zone_id(domain)
        if not zone_id:
            # List available zones
            zones = self.api.request('GET', '/zones')
            if isinstance(zones, list) and zones:
                print(f"Error: Domain '{domain}' not found in your Cloudflare account")
                print("Available domains:")
                for zone in zones[:10]:  # Show first 10
                    print(f"  - {zone['name']}")
                if len(zones) > 10:
                    print(f"  ... and {len(zones) - 10} more")
            raise Exception(f"Domain '{domain}' not found in your Cloudflare account")
        
        # Create route
        route_data = {
            "pattern": pattern,
            "script": worker_name
        }
        
        result = self.api.request('POST', f'/zones/{zone_id}/workers/routes', json=route_data)
        print(f"✓ Route '{pattern}' added for worker '{worker_name}'")
        return result
    
    def list_routes(self, worker_name: Optional[str] = None) -> List[dict]:
        """List routes, optionally filtered by worker"""
        # Need to get all zones and check routes for each
        zones = self.api.request('GET', '/zones')
        all_routes = []
        
        if isinstance(zones, list):
            for zone in zones:
                try:
                    routes = self.api.request('GET', f'/zones/{zone["id"]}/workers/routes')
                    if isinstance(routes, list):
                        for route in routes:
                            route['zone_name'] = zone['name']
                            if not worker_name or route.get('script') == worker_name:
                                all_routes.append(route)
                except:
                    continue
        
        return all_routes

class CLI:
    """Command Line Interface"""
    
    def __init__(self, skip_auth_check=False):
        if not skip_auth_check:
            self.api = CloudflareAPI()
            self.worker_manager = WorkerManager(self.api)
            self.do_manager = DurableObjectManager(self.api, self.worker_manager)
            self.route_manager = RouteManager(self.api)
    
    def auth_init(self):
        """Initialize authentication"""
        print("Cloudflare CLI Authentication Setup")
        print("-" * 40)
        
        api_token = input("API Token: ").strip()
        account_id = input("Account ID: ").strip()
        
        # Test credentials
        test_api = CloudflareAPI()
        test_api.api_token = api_token
        test_api.account_id = account_id
        test_api.headers["Authorization"] = f"Bearer {api_token}"
        
        try:
            test_api.request('GET', f'/accounts/{account_id}')
            print("✓ Authentication successful")
            
            # Save config
            config = {
                "api_token": api_token,
                "account_id": account_id
            }
            test_api.save_config(config)
            print(f"✓ Configuration saved to {CONFIG_FILE}")
            
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            sys.exit(1)
    
    def create_worker(self, args):
        """Handle create worker command"""
        self.worker_manager.create_worker(args.name, args.path)
    
    def deploy(self, args):
        """Handle deploy command"""
        self.worker_manager.deploy(args.name)
    
    def list_workers(self, args):
        """Handle list workers command"""
        workers = self.worker_manager.list_workers()
        
        if args.json:
            print(json.dumps(workers, indent=2))
        else:
            if not workers:
                print("No workers found")
            else:
                print(f"Workers ({len(workers)}):")
                for worker in workers:
                    print(f"  - {worker.get('id', 'unknown')}")
                    if 'created_on' in worker:
                        created = worker['created_on'][:10]
                        print(f"    Created: {created}")
    
    def delete_worker(self, args):
        """Handle delete worker command"""
        if not args.force:
            confirm = input(f"Delete worker '{args.name}'? (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled")
                return
        
        self.worker_manager.delete_worker(args.name)
    
    def create_durable_object(self, args):
        """Handle create durable object command"""
        worker_name = args.worker or args.binding.lower().replace('_', '-')
        self.do_manager.create_durable_object(worker_name, args.binding, args.class_name)
    
    def add_route(self, args):
        """Handle add route command"""
        self.route_manager.add_route(args.pattern, args.worker)
    
    def list_routes(self, args):
        """Handle list routes command"""
        routes = self.route_manager.list_routes(args.worker)
        
        if args.json:
            print(json.dumps(routes, indent=2))
        else:
            if not routes:
                print("No routes found")
            else:
                print(f"Routes ({len(routes)}):")
                for route in routes:
                    print(f"  - {route.get('pattern', 'unknown')} -> {route.get('script', 'none')}")
                    if 'zone_name' in route:
                        print(f"    Zone: {route['zone_name']}")
    
    def tail_logs(self, args):
        """Handle tail logs command"""
        print(f"Tailing logs for worker '{args.name}'...")
        print("Note: This requires wrangler to be installed")
        
        cmd = ["wrangler", "tail", args.name]
        if args.filter:
            cmd.extend(["--filter", args.filter])
        
        try:
            subprocess.run(cmd)
        except FileNotFoundError:
            print("Error: wrangler not found. Install with: npm install -g wrangler")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Cloudflare Workers CLI - Manage Workers, Durable Objects, Routes, and KV Storage"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Auth command
    auth_parser = subparsers.add_parser('auth', help='Authentication commands')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command')
    auth_init_parser = auth_subparsers.add_parser('init', help='Initialize authentication')
    
    # Worker commands
    create_parser = subparsers.add_parser('create', help='Create resources')
    create_subparsers = create_parser.add_subparsers(dest='resource')
    
    # Create worker
    worker_parser = create_subparsers.add_parser('worker', help='Create and deploy a worker')
    worker_parser.add_argument('name', help='Worker name')
    worker_parser.add_argument('--path', required=True, help='Path to worker files')
    
    # Create durable object
    do_parser = create_subparsers.add_parser('durable-object', help='Create a durable object binding')
    do_parser.add_argument('binding', help='Binding name (e.g., CELL_REGISTRY)')
    do_parser.add_argument('--class', dest='class_name', required=True, help='Class name')
    do_parser.add_argument('--worker', help='Worker name (defaults to binding name)')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy a worker')
    deploy_parser.add_argument('name', help='Worker name')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List resources')
    list_subparsers = list_parser.add_subparsers(dest='resource')
    
    workers_list_parser = list_subparsers.add_parser('workers', help='List all workers')
    workers_list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    routes_list_parser = list_subparsers.add_parser('routes', help='List routes')
    routes_list_parser.add_argument('--worker', help='Filter by worker name')
    routes_list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete resources')
    delete_subparsers = delete_parser.add_subparsers(dest='resource')
    
    worker_delete_parser = delete_subparsers.add_parser('worker', help='Delete a worker')
    worker_delete_parser.add_argument('name', help='Worker name')
    worker_delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add resources')
    add_subparsers = add_parser.add_subparsers(dest='resource')
    
    route_parser = add_subparsers.add_parser('route', help='Add a route')
    route_parser.add_argument('pattern', help='Route pattern (e.g., *.example.com/*)')
    route_parser.add_argument('--worker', required=True, help='Worker name')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Tail worker logs')
    logs_parser.add_argument('name', help='Worker name')
    logs_parser.add_argument('--filter', help='Filter expression')
    logs_parser.add_argument('--tail', action='store_true', default=True, help='Follow logs (default)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'auth' and args.auth_command == 'init':
        cli = CLI(skip_auth_check=True)
        cli.auth_init()
        return
    else:
        cli = CLI()
    
    if args.command == 'create':
        if args.resource == 'worker':
            cli.create_worker(args)
        elif args.resource == 'durable-object':
            cli.create_durable_object(args)
    elif args.command == 'deploy':
        cli.deploy(args)
    elif args.command == 'list':
        if args.resource == 'workers':
            cli.list_workers(args)
        elif args.resource == 'routes':
            cli.list_routes(args)
    elif args.command == 'delete':
        if args.resource == 'worker':
            cli.delete_worker(args)
    elif args.command == 'add':
        if args.resource == 'route':
            cli.add_route(args)
    elif args.command == 'logs':
        cli.tail_logs(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)