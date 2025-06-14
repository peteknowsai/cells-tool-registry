#!/usr/bin/env python3
"""
Dice Roller CLI - A simple dice rolling tool for tabletop gaming.

Roll various types of dice with modifiers and special rules.
"""

import argparse
import json
import sys
from typing import List

from parser import DiceParser
from roller import DiceRoller, RollResult


def format_roll_result(result: RollResult, show_rolls: bool = False) -> str:
    """Format a roll result for display.
    
    Args:
        result: The RollResult to format
        show_rolls: Whether to show individual dice rolls
        
    Returns:
        Formatted string
    """
    lines = []
    
    if show_rolls:
        lines.append(f"Rolling {result.expression}:")
        for dr in result.dice_results:
            roll_str = f"  {dr.dice_notation}: {dr.rolls}"
            if dr.dropped_rolls:
                roll_str += f" (kept: {dr.kept_rolls}, dropped: {dr.dropped_rolls})"
            roll_str += f" = {dr.subtotal}"
            lines.append(roll_str)
        if result.modifier != 0:
            lines.append(f"  Modifier: {result.modifier:+d}")
        lines.append(f"Total: {result.total}")
    else:
        lines.append(f"{result.expression} = {result.total}")
    
    return '\n'.join(lines)


def roll_command(args):
    """Handle the roll command."""
    parser = DiceParser()
    roller = DiceRoller()
    
    try:
        # Handle advantage/disadvantage
        if args.advantage and args.disadvantage:
            print("Error: Cannot use both advantage and disadvantage", file=sys.stderr)
            sys.exit(1)
        
        results = []
        
        if args.advantage:
            # Roll with advantage
            for _ in range(args.repeat):
                result = roller.roll_with_advantage()
                results.append(result)
        elif args.disadvantage:
            # Roll with disadvantage
            for _ in range(args.repeat):
                result = roller.roll_with_disadvantage()
                results.append(result)
        else:
            # Parse and roll expressions
            expressions = parser.parse_multiple(args.expression)
            for _ in range(args.repeat):
                for expr in expressions:
                    result = roller.roll(expr)
                    results.append(result)
        
        # Output results
        if args.json:
            output = {
                'rolls': [r.to_dict() for r in results],
                'count': len(results)
            }
            print(json.dumps(output, indent=2))
        else:
            for i, result in enumerate(results):
                if args.repeat > 1:
                    print(f"Roll {i+1}:")
                print(format_roll_result(result, args.show_rolls))
                if i < len(results) - 1:
                    print()
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def stats_command(args):
    """Handle the stats command."""
    parser = DiceParser()
    
    try:
        expression = parser.parse(args.expression)
        
        # Calculate statistics
        min_roll = 0
        max_roll = 0
        
        for dice_set in expression.dice_sets:
            if dice_set.keep_highest:
                # Keep highest N of M dice
                max_roll += dice_set.keep_highest * dice_set.sides
                min_roll += dice_set.keep_highest  # Minimum 1 per kept die
            elif dice_set.drop_lowest:
                # Drop lowest N of M dice
                kept = dice_set.count - dice_set.drop_lowest
                max_roll += kept * dice_set.sides
                min_roll += kept  # Minimum 1 per kept die
            else:
                max_roll += dice_set.count * dice_set.sides
                min_roll += dice_set.count  # Minimum 1 per die
        
        min_total = min_roll + expression.modifier
        max_total = max_roll + expression.modifier
        
        # Calculate average (simplified)
        avg_roll = 0
        for dice_set in expression.dice_sets:
            avg_per_die = (dice_set.sides + 1) / 2
            if dice_set.keep_highest:
                # Approximation for advantage-like mechanics
                kept_dice = dice_set.keep_highest
                avg_roll += kept_dice * avg_per_die * 1.3  # Rough approximation
            elif dice_set.drop_lowest:
                kept_dice = dice_set.count - dice_set.drop_lowest
                avg_roll += kept_dice * avg_per_die * 1.2  # Rough approximation
            else:
                avg_roll += dice_set.count * avg_per_die
        
        avg_total = avg_roll + expression.modifier
        
        if args.json:
            output = {
                'expression': str(expression),
                'minimum': min_total,
                'maximum': max_total,
                'average': round(avg_total, 2)
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Statistics for {expression}:")
            print(f"  Minimum: {min_total}")
            print(f"  Maximum: {max_total}")
            print(f"  Average: {avg_total:.2f}")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Dice Roller - A simple dice rolling CLI tool for tabletop gaming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dice-roller roll d20
  dice-roller roll 3d6+2
  dice-roller roll 4d6kh3  # Roll 4d6, keep highest 3
  dice-roller roll d20 --advantage
  dice-roller roll 2d10,1d8+3 --show-rolls
  dice-roller stats 3d6+2
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Roll command
    roll_parser = subparsers.add_parser('roll', help='Roll dice')
    roll_parser.add_argument('expression', nargs='?', default='d20',
                           help='Dice notation (e.g., 3d6+2, d20, 4d6kh3)')
    roll_parser.add_argument('-a', '--advantage', action='store_true',
                           help='Roll with advantage (2d20, keep highest)')
    roll_parser.add_argument('-d', '--disadvantage', action='store_true',
                           help='Roll with disadvantage (2d20, keep lowest)')
    roll_parser.add_argument('-r', '--repeat', type=int, default=1,
                           help='Repeat the roll N times')
    roll_parser.add_argument('-s', '--show-rolls', action='store_true',
                           help='Show individual dice results')
    roll_parser.add_argument('-j', '--json', action='store_true',
                           help='Output in JSON format')
    roll_parser.set_defaults(func=roll_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics for a dice expression')
    stats_parser.add_argument('expression', help='Dice notation (e.g., 3d6+2)')
    stats_parser.add_argument('-j', '--json', action='store_true',
                            help='Output in JSON format')
    stats_parser.set_defaults(func=stats_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()