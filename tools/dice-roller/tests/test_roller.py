#!/usr/bin/env python3
"""Tests for the dice roller."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import DiceParser, DiceExpression, DiceSet
from roller import DiceRoller, RollResult


class TestDiceRoller:
    """Test cases for DiceRoller."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DiceParser()
        # Create a deterministic roller for testing
        self.test_sequence = []
        self.test_index = 0
        
        def test_random(sides):
            if self.test_index < len(self.test_sequence):
                result = self.test_sequence[self.test_index]
                self.test_index += 1
                return result
            return 1  # Default to 1 if no test sequence
        
        self.roller = DiceRoller(random_func=test_random)
    
    def test_roll_single_die(self):
        """Test rolling a single die."""
        self.test_sequence = [15]
        self.test_index = 0
        
        expr = self.parser.parse("d20")
        result = self.roller.roll(expr)
        
        assert result.total == 15
        assert len(result.dice_results) == 1
        assert result.dice_results[0].rolls == [15]
        assert result.dice_results[0].subtotal == 15
    
    def test_roll_multiple_dice(self):
        """Test rolling multiple dice."""
        self.test_sequence = [4, 2, 6]
        self.test_index = 0
        
        expr = self.parser.parse("3d6")
        result = self.roller.roll(expr)
        
        assert result.total == 12
        assert result.dice_results[0].rolls == [4, 2, 6]
        assert result.dice_results[0].subtotal == 12
    
    def test_roll_with_modifier(self):
        """Test rolling with modifiers."""
        self.test_sequence = [5, 3]
        self.test_index = 0
        
        expr = self.parser.parse("2d6+3")
        result = self.roller.roll(expr)
        
        assert result.total == 11  # 5 + 3 + 3
        assert result.modifier == 3
    
    def test_roll_keep_highest(self):
        """Test keep highest mechanics."""
        self.test_sequence = [2, 6, 4, 5]
        self.test_index = 0
        
        expr = self.parser.parse("4d6kh3")
        result = self.roller.roll(expr)
        
        assert result.total == 15  # 6 + 5 + 4
        assert set(result.dice_results[0].kept_rolls) == {6, 4, 5}
        assert result.dice_results[0].dropped_rolls == [2]
    
    def test_roll_drop_lowest(self):
        """Test drop lowest mechanics."""
        self.test_sequence = [2, 6, 4, 5]
        self.test_index = 0
        
        expr = self.parser.parse("4d6dl1")
        result = self.roller.roll(expr)
        
        assert result.total == 15  # 6 + 4 + 5
        assert set(result.dice_results[0].kept_rolls) == {6, 4, 5}
        assert result.dice_results[0].dropped_rolls == [2]
    
    def test_roll_with_advantage(self):
        """Test advantage rolls."""
        self.test_sequence = [8, 15]
        self.test_index = 0
        
        result = self.roller.roll_with_advantage()
        
        assert result.total == 15  # Keep highest
        assert len(result.dice_results[0].rolls) == 2
        assert result.dice_results[0].kept_rolls == [15]
        assert result.dice_results[0].dropped_rolls == [8]
    
    def test_roll_with_disadvantage(self):
        """Test disadvantage rolls."""
        self.test_sequence = [8, 15]
        self.test_index = 0
        
        result = self.roller.roll_with_disadvantage()
        
        assert result.total == 8  # Keep lowest
        assert len(result.dice_results[0].rolls) == 2
        assert result.dice_results[0].kept_rolls == [8]
        assert result.dice_results[0].dropped_rolls == [15]
    
    def test_complex_expression(self):
        """Test rolling complex expressions."""
        self.test_sequence = [18, 4, 3]
        self.test_index = 0
        
        expr = self.parser.parse("1d20+2d6+5")
        result = self.roller.roll(expr)
        
        assert result.total == 30  # 18 + 4 + 3 + 5
        assert len(result.dice_results) == 2
        assert result.modifier == 5
    
    def test_result_to_dict(self):
        """Test JSON serialization."""
        self.test_sequence = [4, 2, 6]
        self.test_index = 0
        
        expr = self.parser.parse("3d6+2")
        result = self.roller.roll(expr)
        data = result.to_dict()
        
        assert data['expression'] == "3d6+2"
        assert data['total'] == 14
        assert data['modifier'] == 2
        assert len(data['dice_results']) == 1
        assert data['dice_results'][0]['rolls'] == [4, 2, 6]
        assert data['dice_results'][0]['subtotal'] == 12
    
    def test_dice_bounds(self):
        """Test that rolls are within valid bounds."""
        # Use real random roller
        real_roller = DiceRoller()
        
        # Test various dice types
        for sides in [4, 6, 8, 10, 12, 20, 100]:
            expr = DiceExpression(dice_sets=[DiceSet(count=10, sides=sides)])
            result = real_roller.roll(expr)
            
            for roll in result.dice_results[0].rolls:
                assert 1 <= roll <= sides