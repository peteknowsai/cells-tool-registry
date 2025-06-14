#!/usr/bin/env python3
"""Dice rolling logic for the dice-roller CLI tool."""

import random
from dataclasses import dataclass
from typing import List, Optional, Callable

from parser import DiceExpression, DiceSet


@dataclass
class DiceSetResult:
    """Results from rolling a single dice set."""
    dice_notation: str
    rolls: List[int]
    kept_rolls: List[int]
    dropped_rolls: List[int]
    subtotal: int


@dataclass
class RollResult:
    """Complete result from rolling a dice expression."""
    expression: str
    total: int
    dice_results: List[DiceSetResult]
    modifier: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'expression': self.expression,
            'total': self.total,
            'modifier': self.modifier,
            'dice_results': [
                {
                    'dice_notation': dr.dice_notation,
                    'rolls': dr.rolls,
                    'kept_rolls': dr.kept_rolls,
                    'dropped_rolls': dr.dropped_rolls,
                    'subtotal': dr.subtotal
                }
                for dr in self.dice_results
            ]
        }


class DiceRoller:
    """Handles dice rolling operations."""
    
    def __init__(self, random_func: Optional[Callable[[int], int]] = None):
        """Initialize the roller.
        
        Args:
            random_func: Optional custom random function for testing
        """
        self.random_func = random_func or self._default_random
    
    def _default_random(self, sides: int) -> int:
        """Default random number generator."""
        return random.randint(1, sides)
    
    def roll_dice_set(self, dice_set: DiceSet) -> DiceSetResult:
        """Roll a single set of dice.
        
        Args:
            dice_set: The DiceSet to roll
            
        Returns:
            DiceSetResult with all roll information
        """
        # Roll all dice
        rolls = [self.random_func(dice_set.sides) for _ in range(dice_set.count)]
        
        # Sort for keep/drop operations
        sorted_rolls = sorted(rolls, reverse=True)
        
        # Determine which dice to keep
        kept_rolls = rolls[:]
        dropped_rolls = []
        
        if dice_set.keep_highest is not None:
            # Keep only the highest N dice
            kept_indices = set()
            for i in range(dice_set.keep_highest):
                for j, roll in enumerate(rolls):
                    if j not in kept_indices and roll == sorted_rolls[i]:
                        kept_indices.add(j)
                        break
            
            kept_rolls = [rolls[i] for i in sorted(kept_indices)]
            dropped_rolls = [rolls[i] for i in range(len(rolls)) if i not in kept_indices]
        
        elif dice_set.drop_lowest is not None:
            # Drop the lowest N dice
            dropped_indices = set()
            reversed_sorted = sorted_rolls[::-1]
            for i in range(dice_set.drop_lowest):
                for j, roll in enumerate(rolls):
                    if j not in dropped_indices and roll == reversed_sorted[i]:
                        dropped_indices.add(j)
                        break
            
            kept_rolls = [rolls[i] for i in range(len(rolls)) if i not in dropped_indices]
            dropped_rolls = [rolls[i] for i in sorted(dropped_indices)]
        
        subtotal = sum(kept_rolls)
        
        return DiceSetResult(
            dice_notation=str(dice_set),
            rolls=rolls,
            kept_rolls=kept_rolls,
            dropped_rolls=dropped_rolls,
            subtotal=subtotal
        )
    
    def roll(self, expression: DiceExpression) -> RollResult:
        """Roll a complete dice expression.
        
        Args:
            expression: The DiceExpression to roll
            
        Returns:
            RollResult with complete roll information
        """
        dice_results = []
        total = expression.modifier
        
        for dice_set in expression.dice_sets:
            result = self.roll_dice_set(dice_set)
            dice_results.append(result)
            total += result.subtotal
        
        return RollResult(
            expression=str(expression),
            total=total,
            dice_results=dice_results,
            modifier=expression.modifier
        )
    
    def roll_with_advantage(self, sides: int = 20) -> RollResult:
        """Roll with advantage (2 dice, keep highest).
        
        Args:
            sides: Number of sides on the die (default 20)
            
        Returns:
            RollResult for the advantage roll
        """
        dice_set = DiceSet(count=2, sides=sides, keep_highest=1)
        expression = DiceExpression(dice_sets=[dice_set])
        return self.roll(expression)
    
    def roll_with_disadvantage(self, sides: int = 20) -> RollResult:
        """Roll with disadvantage (2 dice, keep lowest).
        
        Args:
            sides: Number of sides on the die (default 20)
            
        Returns:
            RollResult for the disadvantage roll
        """
        # For disadvantage, we roll 2 dice and drop the highest (keep lowest)
        dice_set = DiceSet(count=2, sides=sides, drop_lowest=1)
        # Convert to keep notation internally 
        dice_set.keep_highest = 1
        dice_set.drop_lowest = None
        expression = DiceExpression(dice_sets=[dice_set])
        
        # Roll and manually adjust for disadvantage
        result = self.roll(expression)
        
        # Fix the result to actually keep the lowest
        for dr in result.dice_results:
            all_rolls = dr.rolls[:]
            lowest = min(all_rolls)
            highest = max(all_rolls)
            dr.kept_rolls = [lowest]
            dr.dropped_rolls = [highest]
            dr.subtotal = lowest
            dr.dice_notation = "2d20dl1"  # Correct notation
        
        result.total = result.dice_results[0].subtotal + result.modifier
        result.expression = "2d20dl1"
        return result