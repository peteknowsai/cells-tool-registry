#!/usr/bin/env python3
"""Dice notation parser for the dice-roller CLI tool."""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class DiceSet:
    """Represents a set of dice to roll."""
    count: int
    sides: int
    keep_highest: Optional[int] = None
    drop_lowest: Optional[int] = None
    
    def __str__(self):
        base = f"{self.count}d{self.sides}"
        if self.keep_highest:
            base += f"kh{self.keep_highest}"
        elif self.drop_lowest:
            base += f"dl{self.drop_lowest}"
        return base


@dataclass
class DiceExpression:
    """Represents a complete dice rolling expression."""
    dice_sets: List[DiceSet]
    modifier: int = 0
    
    def __str__(self):
        parts = [str(ds) for ds in self.dice_sets]
        if self.modifier > 0:
            parts.append(f"+{self.modifier}")
        elif self.modifier < 0:
            parts.append(str(self.modifier))
        return "".join(parts)


class DiceParser:
    """Parser for dice notation strings."""
    
    # Regex patterns for parsing
    DICE_PATTERN = re.compile(
        r'(?P<count>\d*)d(?P<sides>\d+)'
        r'(?:kh(?P<keep_high>\d+)|kl(?P<keep_low>\d+)|'
        r'dl(?P<drop_low>\d+)|dh(?P<drop_high>\d+))?'
    )
    MODIFIER_PATTERN = re.compile(r'([+-]\d+)$')
    
    def parse(self, expression: str) -> DiceExpression:
        """Parse a dice expression string.
        
        Args:
            expression: Dice notation string (e.g., "3d6+2", "1d20", "4d6kh3")
            
        Returns:
            DiceExpression object representing the parsed expression
            
        Raises:
            ValueError: If the expression is invalid
        """
        if not expression:
            raise ValueError("Empty dice expression")
            
        # Clean the expression
        expression = expression.strip().lower()
        
        # Extract modifier if present
        modifier = 0
        modifier_match = self.MODIFIER_PATTERN.search(expression)
        if modifier_match:
            modifier = int(modifier_match.group(1))
            expression = expression[:modifier_match.start()]
        
        # Parse dice sets
        dice_sets = []
        for match in self.DICE_PATTERN.finditer(expression):
            count = int(match.group('count') or 1)
            sides = int(match.group('sides'))
            
            if count < 1:
                raise ValueError(f"Invalid dice count: {count}")
            if sides < 1:
                raise ValueError(f"Invalid dice sides: {sides}")
            
            # Handle keep/drop modifiers
            keep_highest = None
            drop_lowest = None
            
            if match.group('keep_high'):
                keep_highest = int(match.group('keep_high'))
                if keep_highest > count:
                    raise ValueError(f"Cannot keep {keep_highest} dice from {count} rolled")
            elif match.group('keep_low'):
                # Convert keep lowest to drop highest
                keep_lowest = int(match.group('keep_low'))
                if keep_lowest < count:
                    drop_lowest = count - keep_lowest
            elif match.group('drop_low'):
                drop_lowest = int(match.group('drop_low'))
                if drop_lowest >= count:
                    raise ValueError(f"Cannot drop {drop_lowest} dice from {count} rolled")
            elif match.group('drop_high'):
                # Convert drop highest to keep lowest
                drop_highest = int(match.group('drop_high'))
                if drop_highest < count:
                    keep_highest = count - drop_highest
            
            dice_set = DiceSet(
                count=count,
                sides=sides,
                keep_highest=keep_highest,
                drop_lowest=drop_lowest
            )
            dice_sets.append(dice_set)
        
        if not dice_sets:
            raise ValueError(f"No valid dice notation found in: {expression}")
        
        return DiceExpression(dice_sets=dice_sets, modifier=modifier)
    
    def parse_multiple(self, expression: str) -> List[DiceExpression]:
        """Parse multiple comma-separated dice expressions.
        
        Args:
            expression: Comma-separated dice notations
            
        Returns:
            List of DiceExpression objects
        """
        expressions = []
        for part in expression.split(','):
            part = part.strip()
            if part:
                expressions.append(self.parse(part))
        
        if not expressions:
            raise ValueError("No valid expressions found")
            
        return expressions