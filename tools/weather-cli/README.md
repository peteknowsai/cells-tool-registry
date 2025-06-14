# Weather CLI

A command-line weather tool that shows current weather and forecasts using OpenWeatherMap API.

## Installation

```bash
# From the registry
./install.sh weather-cli

# Or manually
cd tools/weather-cli
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration

Set your API key:
```bash
weather-cli config --set-key YOUR_API_KEY
```

Or use environment variable:
```bash
export OPENWEATHERMAP_API_KEY=your_key_here
```

Get your API key at: https://openweathermap.org/api

## Usage

### Basic Commands

```bash
# Get current weather
weather-cli current --city London
weather-cli current --city "New York,US"
weather-cli current --coords 51.5074,-0.1278

# Get forecast
weather-cli forecast --city Tokyo --days 3
weather-cli forecast --city "San Francisco" --days 5 --units imperial

# Configure API key
weather-cli config --set-key YOUR_API_KEY
weather-cli config --show
```

### Examples

```bash
# Current weather with metric units (default)
weather-cli current --city Paris

# Current weather with imperial units
weather-cli current --city Miami --units imperial

# Weather forecast for 5 days
weather-cli forecast --city Berlin --days 5

# JSON output for scripting
weather-cli current --city London --json | jq '.current.temperature'

# Use coordinates instead of city name
weather-cli current --coords 35.6762,139.6503  # Tokyo

# Bypass cache for fresh data
weather-cli current --city Rome --no-cache
```

## Features

- Current weather for any city worldwide
- 5-day weather forecast with daily summaries
- Support for metric and imperial units
- Temperature, humidity, wind speed, and conditions
- JSON output for scripting and automation
- Smart caching to reduce API calls (5-minute cache)
- Beautiful terminal output with Rich formatting
- Sunrise/sunset times
- Wind direction and speed
- Atmospheric pressure and cloud coverage

## Command Reference

### `weather-cli current`
Get current weather conditions.

Options:
- `--city, -c`: City name (e.g., 'London' or 'London,GB')
- `--coords`: Coordinates as 'lat,lon' (e.g., '51.5074,-0.1278')
- `--units, -u`: Temperature units (metric/imperial, default: metric)
- `--json, -j`: Output as JSON
- `--no-cache`: Bypass cache and fetch fresh data

### `weather-cli forecast`
Get weather forecast up to 5 days.

Options:
- `--city, -c`: City name (e.g., 'London' or 'London,GB')
- `--coords`: Coordinates as 'lat,lon' (e.g., '51.5074,-0.1278')
- `--days, -d`: Number of days (1-5, default: 3)
- `--units, -u`: Temperature units (metric/imperial, default: metric)
- `--json, -j`: Output as JSON
- `--no-cache`: Bypass cache and fetch fresh data

### `weather-cli config`
Configure the tool.

Options:
- `--set-key`: Set OpenWeatherMap API key
- `--show`: Show current configuration

## API Limitations

- Rate limit: 60 calls/minute
- Free tier: 1,000,000 calls/month
- Forecast limited to 5 days
- Data updates every 10 minutes

## Caching

Weather data is cached for 5 minutes to reduce API calls and improve performance. Cache is stored in `~/.weather-cli/cache.db`. Use `--no-cache` to force fresh data retrieval.

## Error Handling

The tool provides clear error messages for common issues:
- Invalid API key
- City not found
- Network errors
- Rate limit exceeded

## Tips

1. Use country codes to disambiguate cities: `--city "London,GB"` vs `--city "London,CA"`
2. Coordinates are more precise than city names
3. JSON output is perfect for scripting and automation
4. The cache significantly improves response time for repeated queries