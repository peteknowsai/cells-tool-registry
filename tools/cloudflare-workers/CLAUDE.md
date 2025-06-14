# Cloudflare Workers CLI - AI Instructions

## When to Use This Tool

Use `cf-cli` when the user needs to:
- Deploy or manage Cloudflare Workers
- Configure Durable Objects
- Set up custom routes or domains
- Manage KV namespaces (future)
- Work with Workers at the edge

## Key Commands for Common Tasks

### Deploying a Worker
```bash
# From specific path
cf-cli create worker name --path ./path/to/worker

# Auto-detect path
cf-cli deploy worker-name
```

### Setting up Durable Objects
```bash
# The CLI auto-detects DO classes during deployment
# But can also add manually:
cf-cli create durable-object BINDING_NAME --class ClassName
```

### Configuring Routes
```bash
# Automatically finds zone ID
cf-cli add route "*.domain.com/*" --worker worker-name
```

## Integration Patterns

### With Other Tools
```bash
# Deploy worker then configure domain
cf-cli create worker api --path ./api
cf-cli add route "api.example.com/*" --worker api

# Check deployment
cf-cli list workers --json | jq '.[] | select(.id=="api")'
```

### Automation
```bash
# CI/CD deployment
export CLOUDFLARE_API_TOKEN=$CF_TOKEN
export CLOUDFLARE_ACCOUNT_ID=$CF_ACCOUNT

cf-cli deploy my-worker
cf-cli add route "$DEPLOY_DOMAIN/*" --worker my-worker
```

## Important Implementation Details

1. **Durable Objects are not created separately** - They're configured as part of worker deployment via metadata. The CLI abstracts this complexity.

2. **Auto-detection** - The CLI automatically detects DO classes in worker code during deployment.

3. **Zone ID lookup** - Routes automatically resolve domain to zone ID, no manual lookup needed.

4. **Smart path detection** - Deploy command searches common locations for worker files.

## Error Handling

The tool provides helpful guidance:
- Lists available domains when zone not found
- Shows detected DO classes when class not found
- Suggests auth setup when credentials missing

## Output Formats

- Default: Human-readable
- `--json`: Machine-parsable for automation

## Security Notes

- Credentials stored in `~/.cf-cli/config.json`
- Supports environment variables for CI/CD
- Never logs sensitive information