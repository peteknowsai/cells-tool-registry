# Cells Tool Registry

A public registry of CLI tools created by the Tool Germinator cells. Each tool is a Python-based CLI that wraps various APIs and services.

## 🌱 Available Tools

| Tool | Description | API/Service | Requirements | Install |
|------|-------------|-------------|--------------|---------|
| *Registry is empty - tools will appear here as they are germinated* | | | | |

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