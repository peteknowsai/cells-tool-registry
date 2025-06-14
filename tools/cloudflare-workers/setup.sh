#!/bin/bash
set -e

echo "Setting up Cloudflare Workers CLI..."

# Create virtual environment
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

echo "✓ Setup complete"
echo ""
echo "To use the CLI, first set up authentication:"
echo "  cf-cli auth init"
echo ""
echo "Or set environment variables:"
echo "  export CLOUDFLARE_API_TOKEN=your-token"
echo "  export CLOUDFLARE_ACCOUNT_ID=your-account-id"