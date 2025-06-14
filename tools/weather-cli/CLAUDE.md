# Weather CLI - AI Instructions

## When to Use This Tool
- Use when user asks about weather conditions
- Helpful for travel planning or daily weather checks
- Best for current conditions and short-term forecasts
- Useful for comparing weather across multiple locations

## Common Patterns

```bash
# Get current weather
weather-cli current --city "San Francisco" --json | jq '.current'

# Compare temperatures across cities
for city in London Paris Tokyo; do
    echo -n "$city: "
    weather-cli current --city "$city" --json | jq -r '.current.temperature'
done

# Get forecast and extract specific days
weather-cli forecast --city "New York" --days 5 --json | jq '.forecast[2]'

# Monitor weather changes
while true; do
    weather-cli current --city "Seattle" --no-cache
    sleep 300  # Check every 5 minutes
done
```

## Integration Examples

### Combine with other tools
```bash
# Plan outdoor activities based on weather
weather-cli forecast --city "Denver" --days 3 --json | \
    jq -r '.forecast[] | select(.condition | contains("clear") or contains("sunny")) | .date'

# Send weather alerts
if weather-cli current --city "Miami" --json | jq -e '.current.wind.speed > 20'; then
    echo "High wind warning in Miami!"
fi
```

### Automation scripts
```bash
# Daily weather summary
weather-cli current --city "Boston" --json > ~/weather-$(date +%Y%m%d).json

# Weather-based decisions
temp=$(weather-cli current --city "Chicago" --json | jq '.current.temperature')
if (( $(echo "$temp < 0" | bc -l) )); then
    echo "Below freezing - wear warm clothes!"
fi
```

## Error Handling

- Check exit codes: 0 = success, 1 = error
- Parse error messages from stderr
- Invalid API key returns specific error
- Use --no-cache if getting stale data

## Important Notes

1. **API Key Required**: User must configure API key before use
2. **Rate Limits**: Free tier allows 60 calls/minute
3. **Cache Behavior**: Data cached for 5 minutes by default
4. **Location Formats**: 
   - City: "London" or "London,GB"
   - Coordinates: "51.5074,-0.1278"
5. **Units**: Default is metric, use --units imperial for Fahrenheit

## Tips for Best Results

- Always suggest using country codes for ambiguous cities
- Coordinates are more accurate than city names
- JSON output is ideal for parsing specific values
- Cache improves performance for repeated queries
- Forecast data is in 3-hour intervals, aggregated by day