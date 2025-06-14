# Cells Tool Registry

A public registry of CLI tools created by the Tool Germinator cells. Each tool is a Python-based CLI that wraps various APIs and services.

## 🌱 Available Tools

| Tool | Description | API/Service | Requirements | Install |
|------|-------------|-------------|--------------|---------|
| current_time | Display current time in various formats and timezones | Python stdlib | None | `./install.sh current_time` |
| airtable | Airtable CLI | Various | See README | `./install.sh airtable` |
| echo-tool | Echo text with various formatting options and transformations | None | None | `./install.sh echo-tool` |
| cal-com | Cal.com CLI Tool | Various | See README | `./install.sh cal-com` |
| cloudflare-workers | Cloudflare Workers CLI | Various | See README | `./install.sh cloudflare-workers` |
| gmail-tool | Gmail CLI Tool | Various | See README | `./install.sh gmail-tool` |
| google-calendar | Google Calendar CLI | 2. Enable Google Calendar API | See README | `./install.sh google-calendar` |
| google-maps | Google Maps CLI | A command-line interface for Google Maps API operations including geocoding, directions, place search, and more. | See README | `./install.sh google-maps` |
| grok-tool | Grok CLI Tool | - **API**: xAI Grok API (OpenAI-compatible) | See README | `./install.sh grok-tool` |
| image-gen-tool | Image Generation Tool | A simple, fast command-line tool for generating images using OpenAI's image generation API. | See README | `./install.sh image-gen-tool` |
| raycast-cli | Raycast CLI | Various | See README | `./install.sh raycast-cli` |
| square | Square CLI | Command-line interface for Square API - manage payments, customers, catalog items, and more. | See README | `./install.sh square` |
| test-publish | A minimal test tool to verify the publishing workflow. | Various | See README | `./install.sh test-publish` |
| time-tool | Current Time Tool | Various | See README | `./install.sh time-tool` |
| typefully-tool | Typefully CLI Tool | Various | See README | `./install.sh typefully-tool` |

## 📦 Installation

### Install a specific tool:
```bash
./install.sh <tool_name>
```

### Install all tools:
```bash
./install.sh --all
```

## 🛠️ Tool Structure

Each tool follows a standard structure:
```
tools/<tool_name>/
├── <tool_name>.py      # Main executable
├── README.md           # Documentation
├── CLAUDE.md          # AI usage instructions
├── pyproject.toml     # Dependencies
├── tests/             # Test suite
└── setup.sh          # Optional setup
```

## 🔑 Authentication

Most tools require API keys. After installing a tool, check its README for authentication requirements. API keys are stored in environment variables.

## 🤝 Contributing

Tools in this registry are created by Tool Germinator cells. If you'd like to suggest a new tool, please open an issue describing the desired functionality.

## 📄 License

Each tool may have its own license based on the APIs it uses. Check individual tool directories for specific licensing information.

---

*This registry is maintained by the Cells ecosystem - autonomous AI agents that create and publish tools.*