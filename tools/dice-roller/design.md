# Dice Roller CLI Design

## Command Structure

### Main Command
`dice-roller` or `dice`

### Subcommands
1. `roll` - Main rolling command
2. `stats` - Show statistics for a dice expression
3. `history` - Show recent rolls (optional feature)

### Roll Command Options
```
dice-roller roll <expression> [options]

Options:
  -a, --advantage      Roll with advantage (2d20, keep highest)
  -d, --disadvantage   Roll with disadvantage (2d20, keep lowest)
  -r, --repeat N       Repeat the roll N times
  -s, --show-rolls     Show individual dice results
  -j, --json           Output in JSON format
  -h, --help           Show help message
```

### Supported Dice Expressions
1. Basic: `d20`, `3d6`, `2d10+5`
2. Complex: `1d20+2d6-4`
3. Multiple rolls: `3d6+2,1d20+5` (comma-separated)
4. Special notations:
   - `4d6kh3` - Keep highest 3 of 4d6
   - `4d6dl1` - Drop lowest 1 of 4d6
   - `2d20kh1` - Keep highest 1 of 2d20 (advantage)
   - `2d20kl1` - Keep lowest 1 of 2d20 (disadvantage)

## Architecture

### Core Components
1. **Parser Module** (`parser.py`)
   - Parse dice notation strings
   - Support complex expressions
   - Return structured DiceExpression objects

2. **Roller Module** (`roller.py`)
   - Execute rolls based on parsed expressions
   - Support different roll types (normal, advantage, etc.)
   - Track individual die results

3. **CLI Module** (`dice_roller.py`)
   - Main entry point
   - Argument parsing with argparse
   - Format output (text/JSON)

4. **Statistics Module** (`stats.py`)
   - Calculate min/max/average for expressions
   - Show probability distributions

## Data Structures

### DiceExpression
```python
@dataclass
class DiceExpression:
    dice_sets: List[DiceSet]
    modifier: int = 0
    
@dataclass
class DiceSet:
    count: int
    sides: int
    keep_highest: Optional[int] = None
    drop_lowest: Optional[int] = None
```

### RollResult
```python
@dataclass
class RollResult:
    expression: str
    total: int
    dice_results: List[DiceSetResult]
    modifier: int
    
@dataclass
class DiceSetResult:
    dice_notation: str
    rolls: List[int]
    kept_rolls: List[int]
    dropped_rolls: List[int]
    subtotal: int
```

## Error Handling
1. Invalid dice notation → Clear error message
2. Invalid options → Show help
3. Conflicting options → Explain conflict
4. Zero or negative dice → Handle gracefully

## Testing Strategy
1. Unit tests for parser
2. Unit tests for roller
3. Integration tests for CLI
4. Edge case testing
5. Performance testing for large rolls