# Current-Time CLI Tool - AI Instructions

## When to Use This Tool

- Use when user asks about current time, date, or timezone information
- Helpful for scheduling across timezones
- Best for timestamp generation and time format conversion
- Use for debugging timezone-related issues
- Ideal when you need consistent time references

## Common Patterns

```bash
# Get current UTC timestamp for logging
current-time --utc --format iso

# Check time in user's timezone
current-time --tz "America/New_York"

# Quick timezone comparison
current-time --zones "UTC,America/New_York,Asia/Tokyo"

# Generate Unix timestamp
current-time --format unix

# Parse and convert times
current-time convert "2024-06-14 15:30" --from "America/New_York" --to "UTC"
```

## Integration Examples

### Combine with Other Tools

```bash
# Create timestamped backup
TIMESTAMP=$(current-time --format custom --custom-format "%Y%m%d_%H%M%S")
cp important.db backup_${TIMESTAMP}.db

# Log with UTC timestamp
echo "[$(current-time --utc --format iso)] Process started" >> app.log

# Schedule based on timezone
if [[ $(current-time --tz "America/New_York" --format custom --custom-format "%H") -ge 9 ]]; then
  echo "Business hours in New York"
fi
```

### Chain Operations

```bash
# Get all US timezones and their current times
current-time list-zones --filter "America/" --json | \
  jq -r '.timezones[]' | \
  grep -E "(New_York|Chicago|Denver|Los_Angeles)" | \
  xargs -I {} current-time --tz {} --format custom --custom-format "{}: %H:%M %Z"

# Convert multiple timestamps
cat timestamps.txt | while read ts; do
  current-time convert "$ts" --from UTC --to "Europe/London"
done
```

### Parse JSON Output

```bash
# Extract specific fields
current-time --json --verbose --utc | jq '{
  time: .time,
  week: .week_number,
  day_of_year: .day_of_year
}'

# Get time in multiple zones as JSON array
current-time --json --zones "UTC,EST,PST" | jq '.times[] | "\(.timezone): \(.time)"'
```

## Error Handling

```bash
# Check if timezone is valid
if ! current-time --tz "$USER_TZ" >/dev/null 2>&1; then
  echo "Invalid timezone. Available options:"
  current-time list-zones --filter "${USER_TZ:0:3}"
fi

# Fallback to UTC on error
TIME=$(current-time --tz "$TZ" 2>/dev/null || current-time --utc)
```

## Advanced Usage

### Timezone Validation
```bash
# Validate timezone before using
validate_timezone() {
  current-time list-zones --json | jq -r '.timezones[]' | grep -q "^$1$"
}

if validate_timezone "America/New_York"; then
  echo "Valid timezone"
fi
```

### Meeting Scheduler
```bash
# Find good meeting time across timezones
for tz in "America/New_York" "Europe/London" "Asia/Tokyo"; do
  echo -n "$tz: "
  current-time convert "15:00" --from "America/New_York" --to "$tz"
done
```

### Relative Time Calculations
While this tool focuses on current time, for relative time calculations combine with date command:
```bash
# Tomorrow at this time in Tokyo
TOMORROW=$(date -v+1d +"%Y-%m-%d %H:%M")
current-time convert "$TOMORROW" --from "Local" --to "Asia/Tokyo"
```

## Best Practices

1. **Always use --json for automation** - Makes parsing reliable
2. **Specify timezones explicitly** - Don't rely on system timezone
3. **Use ISO format for logs** - Universally parseable
4. **Cache timezone lists** - The list-zones command output rarely changes
5. **Handle timezone errors gracefully** - Suggest alternatives on typos

## Performance Notes

- Timezone list is cached after first call
- JSON output has minimal overhead
- Multiple timezone queries are processed efficiently
- No external API calls means instant responses

## Security Considerations

- No API keys or authentication required
- No network requests made
- All timezone data is local
- Safe to use in automated scripts without rate limit concerns