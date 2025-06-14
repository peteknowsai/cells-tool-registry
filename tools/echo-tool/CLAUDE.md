# Echo Tool - AI Instructions

## When to Use This Tool

- Use when you need to format or transform text output
- Helpful for creating formatted messages, logs, or banners
- Best for text processing tasks that require specific formatting
- Useful for debugging (examining text with counts, boxes, etc.)
- Great for creating visually distinct output in scripts

## Common Patterns

```bash
# Create formatted log entries
echo-tool "Process completed" --prefix "[$(date '+%H:%M:%S')] "

# Create visual separators
echo-tool "=" --repeat 50

# Debug text content
echo-tool "$variable" --count --box

# Process command output
command | echo-tool --upper --prefix "RESULT: "

# Create JSON data for further processing
echo-tool "data" --json | jq '.output'

# Chain transformations
echo-tool "important message" --upper --box --rainbow
```

## Integration Examples

### With Other Tools
```bash
# Format grok output
grok chat "question" | echo-tool --box

# Create timestamped logs
current-time | echo-tool --prefix "Last check: " --output status.log

# Format API responses
curl -s api.example.com | echo-tool --json --count
```

### In Scripts
```bash
#!/bin/bash
# Status reporter
echo-tool "Starting backup..." --prefix "[BACKUP] " --type
# ... backup commands ...
echo-tool "Backup complete!" --prefix "[BACKUP] " --upper --rainbow
```

### For User Feedback
```bash
# Success message
echo-tool "✓ Operation successful" --rainbow --box

# Warning message
echo-tool "⚠ Warning: Low disk space" --upper --repeat 2

# Progress indicator
for i in {1..5}; do
  echo-tool "." --prefix "Processing" --suffix " ($i/5)"
  sleep 1
done
```

## Error Handling

- Check exit codes: 0 for success, 1 for errors
- Errors are written to stderr
- Common errors:
  - No input provided (neither argument nor piped)
  - Invalid file paths for output
  - Permission denied for file operations

## Best Practices

1. **Use --json for automation**: When integrating with other tools, JSON output provides structured data
2. **Combine with current-time**: For timestamped logs and messages
3. **Use --box for important messages**: Makes output stand out
4. **Pipe support**: Echo-tool accepts piped input, making it versatile in command chains
5. **Avoid --type in scripts**: The typing effect is for interactive use only

## Advanced Usage

### Multi-line Processing
```bash
# Process multi-line input with line numbers
printf "First line\nSecond line\nThird line" | echo-tool --line-numbers --box
```

### Conditional Formatting
```bash
# Format based on conditions
if [ $status -eq 0 ]; then
  echo-tool "SUCCESS" --rainbow --box
else
  echo-tool "FAILED" --upper --repeat 3 --prefix "ERROR: "
fi
```

### Log Rotation Helper
```bash
# Append with timestamp, useful for simple logging
echo-tool "Event occurred" \
  --prefix "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] " \
  --append events.log
```

## Notes

- Pure Python implementation ensures cross-platform compatibility
- No external dependencies required
- Rainbow colors require terminal support for ANSI escape codes
- The --type effect adds delays, not suitable for non-interactive use
- File operations respect system permissions