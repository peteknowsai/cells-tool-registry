# Weather CLI Design Document

## CLI Interface Design

### Command Structure
```
weather-cli [command] [options]
```

### Commands

#### 1. `current` - Get current weather
```bash
weather-cli current --city <city> [--units <metric|imperial>] [--json]
weather-cli current --coords <lat,lon> [--units <metric|imperial>] [--json]
```

#### 2. `forecast` - Get weather forecast
```bash
weather-cli forecast --city <city> [--days <1-5>] [--units <metric|imperial>] [--json]
weather-cli forecast --coords <lat,lon> [--days <1-5>] [--units <metric|imperial>] [--json]
```

#### 3. `config` - Configure API key
```bash
weather-cli config --set-key <api_key>
weather-cli config --show
```

### Options
- `--city, -c`: City name (with optional country code)
- `--coords`: Latitude,longitude coordinates
- `--units, -u`: Temperature units (metric/imperial, default: metric)
- `--days, -d`: Number of forecast days (1-5, default: 3)
- `--json, -j`: Output in JSON format
- `--no-cache`: Bypass cache and fetch fresh data
- `--help, -h`: Show help message
- `--version, -v`: Show version

### Architecture

#### Core Components
1. **Main CLI Entry Point** (`weather_cli.py`)
   - Argument parsing with argparse
   - Command routing
   - Error handling

2. **Weather Service** (`WeatherService` class)
   - PyOWM wrapper
   - API call handling
   - Data formatting

3. **Cache Manager** (`CacheManager` class)
   - SQLite-based caching
   - 5-minute expiration
   - Cache key generation

4. **Formatter** (`WeatherFormatter` class)
   - Terminal output with Rich
   - JSON formatting
   - Unit conversion

5. **Config Manager** (`ConfigManager` class)
   - API key storage in ~/.weather-cli/config.json
   - Environment variable support

### Error Handling
- Invalid API key → Clear error message with setup instructions
- City not found → Suggest using coordinates or country code
- Network errors → Retry with exponential backoff
- Rate limit → Show remaining time to wait
- No API key → Prompt to configure

### Caching Strategy
- Cache key: `{city/coords}_{units}_{timestamp_5min_bucket}`
- Store in SQLite: `~/.weather-cli/cache.db`
- Automatic cleanup of expired entries

### Output Formats

#### Terminal Output (Rich)
```
┌─ Current Weather for London, GB ─────────────┐
│ Temperature: 15°C (59°F)                     │
│ Feels Like: 13°C (55°F)                      │
│ Condition: Partly cloudy                     │
│ Humidity: 72%                                │
│ Wind: 5.2 m/s NW                             │
│ Pressure: 1013 hPa                           │
│ Updated: 2025-01-14 10:30 UTC                │
└──────────────────────────────────────────────┘
```

#### JSON Output
```json
{
  "location": {
    "city": "London",
    "country": "GB",
    "coordinates": {"lat": 51.5074, "lon": -0.1278}
  },
  "current": {
    "temperature": 15,
    "feels_like": 13,
    "condition": "Partly cloudy",
    "humidity": 72,
    "wind": {"speed": 5.2, "direction": "NW"},
    "pressure": 1013,
    "timestamp": "2025-01-14T10:30:00Z"
  }
}
```

### Testing Strategy
- Unit tests for each component
- Mock PyOWM API calls
- Test cache behavior
- Test all error conditions
- Integration tests with real API (optional)