# Cloudflare Workers CLI Documentation

## Installation

```bash
# Already installed globally as 'cf-cli'
cf-cli --help
```

## Authentication

```bash
# Initialize authentication
cf-cli auth init

# Or use environment variables
export CLOUDFLARE_API_TOKEN=your-token
export CLOUDFLARE_ACCOUNT_ID=your-account-id
```

## Commands

### Worker Management

```bash
# Create and deploy a worker from local files
cf-cli create worker <name> --path <directory>

# Deploy/update an existing worker
cf-cli deploy <name>

# List all workers
cf-cli list workers [--json]

# Delete a worker
cf-cli delete worker <name> [--force]

# View worker logs (requires wrangler)
cf-cli logs <name> [--filter <expression>]
```

### Durable Objects

```bash
# Create a Durable Object binding
cf-cli create durable-object <binding-name> --class <class-name> [--worker <worker-name>]

# If --worker is omitted, uses binding name as worker name
```

### Routes

```bash
# Add a route pattern to a worker
cf-cli add route <pattern> --worker <worker-name>

# List all routes
cf-cli list routes [--json]

# List routes for a specific worker
cf-cli list routes --worker <worker-name> [--json]
```

## Route Pattern Syntax

- `example.com/*` - All paths on domain
- `*.example.com/*` - All subdomains
- `subdomain.example.com/*` - Specific subdomain
- `example.com/api/*` - Specific path prefix
- `*.example.com/api/*` - Combination of subdomain and path

## Options

- `--json` - Output in JSON format for scripting
- `--force` - Skip confirmation prompts
- `--help` - Show help for any command

## Configuration

Settings are stored in `~/.cf-cli/config.json`

## Exit Codes

- `0` - Success
- `1` - Error (with descriptive message)

## Examples

```bash
# Deploy a worker
cf-cli create worker my-api --path ./src/api-worker

# Add a wildcard route
cf-cli add route "*.api.example.com/*" --worker my-api

# List workers as JSON
cf-cli list workers --json | jq '.[].id'

# Create a Durable Object binding
cf-cli create durable-object USER_STORAGE --class UserStore --worker my-api
```