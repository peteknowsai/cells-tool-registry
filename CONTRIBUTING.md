# Contributing to Cells Tool Registry

## 🌱 How Tools Are Created

Tools in this registry are created by Tool Germinator cells - specialized AI agents that research, develop, test, and publish CLI tools automatically.

## 🤖 Requesting a New Tool

To request a new tool:

1. **Open an Issue** with the title format: `[Tool Request] <tool_name>`
2. **Describe the tool** you'd like:
   - What API or service should it wrap?
   - What commands/features are most important?
   - Any specific use cases you have in mind?

3. **Wait for Germination** - A Tool Germinator cell will:
   - Research the API/service
   - Design the CLI interface
   - Implement and test the tool
   - Publish it to this registry

## 📋 Tool Standards

All tools in this registry follow these standards:

### Structure
```
tools/<tool_name>/
├── <tool_name>.py      # Main executable
├── README.md           # Human documentation
├── CLAUDE.md          # AI usage instructions
├── pyproject.toml     # Dependencies
├── tests/             # Pytest test suite
└── setup.sh          # Optional setup script
```

### Naming
- Use underscores for tool names (e.g., `weather_cli`, `stock_ticker`)
- Avoid reserved names: `cells`, `claude`, `api`, `test`, `tools`

### Features
- Support `--help` flag
- Support `--json` flag for automation
- Use environment variables for API keys
- Include comprehensive error messages
- Exit with proper codes (0 for success, 1+ for errors)

### Documentation
- **README.md** should include:
  - Description
  - Installation instructions
  - Usage examples
  - Configuration/authentication
  - API limitations

- **CLAUDE.md** should include:
  - When to use the tool
  - Integration patterns
  - Automation examples

## 🐛 Reporting Issues

If you find a bug in a tool:
1. Check if the issue already exists
2. Create a new issue with:
   - Tool name and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/output

## 🔄 Tool Updates

Tools may be updated by Tool Germinator cells to:
- Fix bugs
- Add new features
- Update to new API versions
- Improve performance

Updates are automatic and preserve backward compatibility when possible.

## 📄 License

By contributing tool requests or feedback, you agree that:
- Tools may be used by anyone
- Tools are provided as-is
- Individual tools may have specific licenses based on the APIs they use

---

*Remember: This is a living ecosystem of tools created by AI for the benefit of all developers!*