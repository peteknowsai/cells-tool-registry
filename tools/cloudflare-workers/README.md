# Cloudflare Workers CLI

A comprehensive command-line interface for managing Cloudflare Workers, Durable Objects, Routes, and KV Storage.

## Installation

```bash
./install-tool.sh cloudflare-workers
```

Or manually:
```bash
cd cloudflare-workers
./setup.sh
```

## Quick Start

### 1. Authentication

```bash
# Interactive setup
cf-cli auth init

# Or use environment variables
export CLOUDFLARE_API_TOKEN=your-token
export CLOUDFLARE_ACCOUNT_ID=your-account-id
```

### 2. Team's Required Commands

```bash
# Create and deploy a worker
cf-cli create worker cell-router --path ./workers/cell-router

# Deploy updates to existing worker
cf-cli deploy cell-router

# Create Durable Object binding
cf-cli create durable-object CELL_REGISTRY --class CellRegistry

# Add route with wildcard
cf-cli add route "*.cells.fidelity.com" --worker cell-router
```

## Features

### Worker Management

```bash
# Create and deploy worker from local files
cf-cli create worker my-worker --path ./src

# Deploy/update existing worker (searches common paths)
cf-cli deploy my-worker

# List all workers
cf-cli list workers

# Delete a worker
cf-cli delete worker my-worker

# Tail real-time logs (requires wrangler)
cf-cli logs my-worker --tail
```

### Durable Objects

```bash
# Create DO binding (validates class exists in worker)
cf-cli create durable-object BINDING_NAME --class ClassName --worker my-worker

# If --worker is omitted, uses binding name as worker name
cf-cli create durable-object CELL_REGISTRY --class CellRegistry
```

### Routes & Domains

```bash
# Add route pattern (automatically finds zone ID)
cf-cli add route "*.example.com/*" --worker my-worker
cf-cli add route "api.example.com/v1/*" --worker api-worker

# List all routes
cf-cli list routes

# List routes for specific worker
cf-cli list routes --worker my-worker
```

## Project Structure

When creating a worker, the CLI looks for files in this order:
1. `index.js` or `index.ts`
2. `worker.js` or `worker.ts`
3. `{worker-name}.js` or `{worker-name}.ts`

Example structure:
```
workers/
├── cell-router/
│   ├── index.js       # Main worker code
│   └── wrangler.toml  # Optional config
└── api-worker/
    └── worker.js
```

## Durable Objects

The CLI automatically detects Durable Object classes in your code:

```javascript
// Automatically detected patterns:
export class CellRegistry extends DurableObject {
  async fetch(request) {
    // Handle requests
  }
}

// Also detected:
export class MyObject {
  async fetch(request) {
    // Has fetch method
  }
}
```

## Configuration

### Environment Variables
- `CLOUDFLARE_API_TOKEN` - Your API token
- `CLOUDFLARE_ACCOUNT_ID` - Your account ID

### Config File
Stored in `~/.cf-cli/config.json`:
```json
{
  "api_token": "your-token",
  "account_id": "your-account-id"
}
```

## Route Patterns

Supported patterns:
- `example.com/*` - All paths on domain
- `*.example.com/*` - All subdomains
- `api.example.com/v1/*` - Specific path prefix
- `*example.com/api/*` - Domain and subdomains with path

## Error Handling

The CLI provides helpful error messages:
- Missing credentials prompt for auth setup
- Invalid DO classes show available classes
- Missing zones list available domains
- Route conflicts are detected

## API Token Permissions

Your API token needs these permissions:
- Account: Workers Scripts:Edit
- Zone: Workers Routes:Edit
- Zone: Zone:Read

## Troubleshooting

### "Domain not found"
The domain must exist in your Cloudflare account. The CLI will list available domains.

### "Class not found"
Ensure your Durable Object class is exported and extends DurableObject or has a fetch method.

### "Worker not found"
Check that worker files exist in one of the searched paths: `./workers/{name}`, `./{name}`, `./src`, or current directory.

## Examples

### Complete Setup Flow

```bash
# 1. Initialize auth
cf-cli auth init

# 2. Create worker with Durable Objects
cf-cli create worker cell-router --path ./workers/cell-router

# 3. Add DO binding (if not auto-detected)
cf-cli create durable-object CELLS --class CellRegistry --worker cell-router

# 4. Configure routing
cf-cli add route "*.cells.example.com/*" --worker cell-router

# 5. Deploy updates
cf-cli deploy cell-router

# 6. Monitor logs
cf-cli logs cell-router --tail
```

### Bulk Operations (via config file)

Create `.cf-cli.json`:
```json
{
  "workers": {
    "cell-router": {
      "path": "./workers/cell-router",
      "routes": ["*.cells.example.com/*"],
      "durable_objects": [
        {"binding": "CELL_REGISTRY", "class": "CellRegistry"}
      ]
    }
  }
}
```

Then: `cf-cli deploy --all` (future feature)

## Output Formats

```bash
# Human-readable (default)
cf-cli list workers

# JSON output for scripting
cf-cli list workers --json
cf-cli list routes --json
```

## Security

- API tokens are stored in `~/.cf-cli/config.json` with user-only permissions
- Never commit credentials to version control
- Use zone-specific tokens when possible