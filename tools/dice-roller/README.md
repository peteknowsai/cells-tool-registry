# Dice Roller

A simple dice rolling CLI tool for tabletop gaming. Roll various types of dice with modifiers and special rules.

## Installation

```bash
# From the registry
./install.sh dice-roller

# Or manually
cd tools/dice-roller
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

### Basic Commands

```bash
# Roll a single d20
dice-roller roll d20

# Roll 3d6+2
dice-roller roll 3d6+2

# Roll with advantage
dice-roller roll d20 --advantage

# Roll with disadvantage
dice-roller roll d20 --disadvantage

# Show individual dice results
dice-roller roll 3d6+2 --show-rolls

# Repeat rolls
dice-roller roll d20 --repeat 6

# Multiple expressions
dice-roller roll "2d10+5,1d8+3,1d4"
```

### Advanced Dice Notation

```bash
# Keep highest 3 of 4d6 (ability score generation)
dice-roller roll 4d6kh3

# Drop lowest 1 of 4d6 (same as above)
dice-roller roll 4d6dl1

# Roll 2d20 keep highest (advantage)
dice-roller roll 2d20kh1

# Roll 2d20 keep lowest (disadvantage)
dice-roller roll 2d20kl1
```

### Statistics

```bash
# Show min/max/average for an expression
dice-roller stats 3d6+2

# JSON output
dice-roller stats 3d6+2 --json
```

### JSON Output

```bash
# Get results in JSON format for automation
dice-roller roll 3d6+2 --json

# Example output:
{
  "rolls": [
    {
      "expression": "3d6+2",
      "total": 14,
      "modifier": 2,
      "dice_results": [
        {
          "dice_notation": "3d6",
          "rolls": [4, 2, 6],
          "kept_rolls": [4, 2, 6],
          "dropped_rolls": [],
          "subtotal": 12
        }
      ]
    }
  ],
  "count": 1
}
```

## Features

- Standard dice notation (NdX+Y)
- Keep highest/lowest mechanics
- Drop highest/lowest mechanics
- Advantage/disadvantage rolls
- Multiple expressions in one command
- Individual dice result display
- Statistics calculation
- JSON output for automation
- Repeat rolls

## Examples

### Character Creation
```bash
# Roll 6 ability scores
dice-roller roll 4d6kh3 --repeat 6 --show-rolls
```

### Combat
```bash
# Attack with advantage
dice-roller roll d20 --advantage --show-rolls

# Damage roll
dice-roller roll 2d6+4
```

### Complex Rolls
```bash
# Multiple damage types
dice-roller roll "1d8+3,2d6" --show-rolls
```

## Dice Types Supported

- d4, d6, d8, d10, d12, d20
- d100 (or any number of sides)
- Custom dice (e.g., d3, d17, d1000)