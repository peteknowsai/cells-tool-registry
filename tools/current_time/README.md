# Current-Time CLI Tool

A command-line tool for displaying current time in various formats and timezones.

## Installation

```bash
# From the registry
./install.sh current_time

# Or manually
cd tools/current_time
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

No API keys required - this tool uses Python's built-in timezone support.

## Usage

### Basic Commands

```bash
# Display current local time
current-time

# Display UTC time
current-time --utc

# Display time in specific timezone
current-time --tz "America/New_York"

# Display multiple timezones
current-time --zones "UTC,America/New_York,Asia/Tokyo"

# Display all major timezones
current-time --all-zones
```

### Format Options

```bash
# ISO 8601 format
current-time --format iso

# RFC 3339 format
current-time --format rfc3339

# Unix timestamp
current-time --format unix

# Custom format
current-time --format custom --custom-format "%Y-%m-%d %H:%M:%S"

# JSON output (for automation)
current-time --json --utc
```

### Timezone Management

```bash
# List all available timezones
current-time list-zones

# Filter timezones
current-time list-zones --filter America

# List as JSON
current-time list-zones --json
```

### Time Conversion

```bash
# Convert time between timezones
current-time convert "2024-06-14 10:30" --from UTC --to "Asia/Tokyo"

# Convert with JSON output
current-time convert "2024-06-14 10:30" --from UTC --to "America/New_York" --json
```

### Examples

```bash
# Show current time in multiple formats
current-time --format iso --utc
# Output: 2024-06-14T15:30:45.123456+00:00

# Show time in major cities
current-time --zones "America/New_York,Europe/London,Asia/Tokyo" --format custom --custom-format "%H:%M %Z"
# Output:
# America/New_York     11:30 EDT
# Europe/London        16:30 BST
# Asia/Tokyo           00:30 JST

# Get verbose information
current-time --verbose --json --utc
# Output includes week number, day of year, UTC offset, etc.
```

## Features

- Display time in any timezone
- Multiple output formats (ISO 8601, RFC 3339, Unix timestamp, custom)
- Convert times between timezones
- List and filter available timezones
- JSON output support for automation
- Verbose mode with additional time information
- Smart timezone suggestions for typos
- Support for Python 3.7+ (uses zoneinfo on 3.9+, pytz fallback for older versions)

## API Limitations

- None - uses Python's built-in timezone database
- No external API calls required
- No rate limits or usage restrictions

## Technical Notes

- Uses `zoneinfo` module on Python 3.9+ for best performance
- Falls back to `pytz` on older Python versions
- Windows users need `tzdata` package (automatically installed)
- All timezone data is included with Python or installed packages