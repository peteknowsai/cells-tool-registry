# Dice Roller - AI Instructions

## When to Use This Tool

- Use when user mentions rolling dice, random numbers for games, or tabletop RPG mechanics
- Helpful for D&D, Pathfinder, or any dice-based game scenarios
- Best for generating random results with specific constraints
- Use when calculating probabilities or statistics for dice rolls

## Common Patterns

```bash
# Quick d20 roll for skill checks
dice-roller roll d20

# Ability score generation
dice-roller roll 4d6kh3 --repeat 6

# Combat rolls with damage
dice-roller roll d20 --advantage && dice-roller roll 2d6+4

# Check probabilities
dice-roller stats 3d6+2
```

## Integration Examples

### Character Sheet Generation
```bash
# Generate a full set of ability scores
for stat in STR DEX CON INT WIS CHA; do
    result=$(dice-roller roll 4d6kh3 --json | jq -r '.rolls[0].total')
    echo "$stat: $result"
done
```

### Combat Automation
```bash
# Attack with advantage, if hit (AC 15), roll damage
attack=$(dice-roller roll d20 --advantage --json | jq -r '.rolls[0].total')
if [ $attack -ge 15 ]; then
    damage=$(dice-roller roll 1d8+3 --json | jq -r '.rolls[0].total')
    echo "Hit! Damage: $damage"
else
    echo "Miss!"
fi
```

### Batch Rolling
```bash
# Roll initiative for 5 goblins
dice-roller roll d20+2 --repeat 5 --json | jq -r '.rolls[].total' | sort -rn
```

## Advanced Usage

### Parsing Output
```bash
# Extract just the total from a roll
dice-roller roll 3d6+2 --json | jq -r '.rolls[0].total'

# Get all individual dice results
dice-roller roll 3d6 --json | jq -r '.rolls[0].dice_results[0].rolls[]'

# Check for critical hits (natural 20)
result=$(dice-roller roll d20 --json)
total=$(echo $result | jq -r '.rolls[0].total')
rolls=$(echo $result | jq -r '.rolls[0].dice_results[0].rolls[]')
if [ "$rolls" = "20" ]; then
    echo "Critical hit!"
fi
```

### Probability Analysis
```bash
# Compare advantage vs normal roll
echo "Normal d20 stats:"
dice-roller stats d20

echo "Advantage stats:"
dice-roller stats 2d20kh1
```

## Error Handling

- Invalid notation returns clear error messages
- Check exit codes: 0 for success, 1 for errors
- Use --json for consistent parsing in scripts

## Tips

1. Use `--show-rolls` to see individual dice for transparency
2. Use `--json` when integrating with other tools
3. Combine with jq for powerful automation
4. The tool uses system random, not cryptographic random
5. Notation is case-insensitive (D20 = d20)