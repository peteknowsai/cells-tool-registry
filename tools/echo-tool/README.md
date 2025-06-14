# Echo Tool

A versatile command-line tool that echoes input back with various formatting options and transformations.

## Installation

```bash
# From the registry
./install.sh echo-tool

# Or manually
cd tools/echo-tool
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

No configuration required - echo-tool is a standalone utility.

## Usage

### Basic Commands

```bash
# Basic echo
echo-tool "Hello World"

# Transform to uppercase
echo-tool "hello" --upper

# Transform to lowercase
echo-tool "HELLO" --lower

# Title case
echo-tool "hello world" --title

# Reverse text
echo-tool "hello" --reverse
```

### Formatting Options

```bash
# Add prefix and suffix
echo-tool "message" --prefix "[INFO] " --suffix " !!!"

# Repeat multiple times
echo-tool "Important" --repeat 3

# Add line numbers
echo-tool "Line 1\nLine 2\nLine 3" --line-numbers

# Combine options
echo-tool "alert" --upper --repeat 3 --prefix ">>> "
```

### Special Features

```bash
# ASCII art box
echo-tool "Notice" --box

# Rainbow colors (terminal support required)
echo-tool "Colorful text" --rainbow

# Typing effect simulation
echo-tool "Simulating typing..." --type

# Word and character count
echo-tool "Count these words" --count
```

### Output Options

```bash
# Output to file
echo-tool "Log entry" --output log.txt

# Append to file
echo-tool "Another entry" --append log.txt

# JSON output (great for automation)
echo-tool "data" --json

# JSON with counts
echo-tool "analyze this text" --json --count
```

### Piped Input

```bash
# Accept piped input
echo "piped text" | echo-tool --upper

# Process file contents
cat file.txt | echo-tool --box

# Chain with other commands
curl -s https://example.com | echo-tool --count
```

## Features

- Text transformations (upper, lower, title, reverse)
- Flexible formatting (prefix, suffix, repeat)
- Line numbering support
- ASCII art boxes
- Rainbow color effect
- Typing simulation
- Word/character counting
- File output (write or append)
- JSON output for automation
- Pipe-friendly design
- Cross-platform compatibility

## Examples

### Create a formatted log entry
```bash
echo-tool "Server started successfully" \
  --prefix "[$(date '+%Y-%m-%d %H:%M:%S')] " \
  --output server.log
```

### Create a banner
```bash
echo-tool "WELCOME" --box --rainbow
```

### Analyze text statistics
```bash
cat document.txt | echo-tool --count --json | jq '.counts'
```

### Create repeated warnings
```bash
echo-tool "WARNING: System maintenance in 5 minutes" \
  --upper --repeat 3 --prefix "*** " --suffix " ***"
```

## API Limitations

None - echo-tool is a standalone utility with no external dependencies or API requirements.