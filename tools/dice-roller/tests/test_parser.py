#!/usr/bin/env python3
"""Tests for the dice notation parser."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import DiceParser, DiceExpression, DiceSet


class TestDiceParser:
    """Test cases for DiceParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DiceParser()
    
    def test_parse_simple_dice(self):
        """Test parsing simple dice notation."""
        # Single die
        expr = self.parser.parse("d20")
        assert len(expr.dice_sets) == 1
        assert expr.dice_sets[0].count == 1
        assert expr.dice_sets[0].sides == 20
        assert expr.modifier == 0
        
        # Multiple dice
        expr = self.parser.parse("3d6")
        assert expr.dice_sets[0].count == 3
        assert expr.dice_sets[0].sides == 6
    
    def test_parse_with_modifier(self):
        """Test parsing dice with modifiers."""
        # Positive modifier
        expr = self.parser.parse("1d20+5")
        assert expr.dice_sets[0].count == 1
        assert expr.dice_sets[0].sides == 20
        assert expr.modifier == 5
        
        # Negative modifier
        expr = self.parser.parse("2d10-3")
        assert expr.dice_sets[0].count == 2
        assert expr.dice_sets[0].sides == 10
        assert expr.modifier == -3
    
    def test_parse_keep_highest(self):
        """Test parsing keep highest notation."""
        expr = self.parser.parse("4d6kh3")
        assert expr.dice_sets[0].count == 4
        assert expr.dice_sets[0].sides == 6
        assert expr.dice_sets[0].keep_highest == 3
        assert expr.dice_sets[0].drop_lowest is None
    
    def test_parse_drop_lowest(self):
        """Test parsing drop lowest notation."""
        expr = self.parser.parse("4d6dl1")
        assert expr.dice_sets[0].count == 4
        assert expr.dice_sets[0].sides == 6
        assert expr.dice_sets[0].drop_lowest == 1
        assert expr.dice_sets[0].keep_highest is None
    
    def test_parse_multiple_dice_sets(self):
        """Test parsing multiple dice sets."""
        expr = self.parser.parse("1d20+2d6+3")
        assert len(expr.dice_sets) == 2
        assert expr.dice_sets[0].count == 1
        assert expr.dice_sets[0].sides == 20
        assert expr.dice_sets[1].count == 2
        assert expr.dice_sets[1].sides == 6
        assert expr.modifier == 3
    
    def test_parse_multiple_expressions(self):
        """Test parsing comma-separated expressions."""
        expressions = self.parser.parse_multiple("d20,3d6+2,1d8")
        assert len(expressions) == 3
        assert expressions[0].dice_sets[0].sides == 20
        assert expressions[1].dice_sets[0].count == 3
        assert expressions[1].modifier == 2
        assert expressions[2].dice_sets[0].sides == 8
    
    def test_parse_case_insensitive(self):
        """Test that parsing is case insensitive."""
        expr1 = self.parser.parse("3D6+2")
        expr2 = self.parser.parse("3d6+2")
        assert str(expr1) == str(expr2)
    
    def test_parse_errors(self):
        """Test error handling."""
        # Empty expression
        with pytest.raises(ValueError, match="Empty dice expression"):
            self.parser.parse("")
        
        # Invalid dice count
        with pytest.raises(ValueError, match="Invalid dice count"):
            self.parser.parse("0d6")
        
        # Invalid dice sides
        with pytest.raises(ValueError, match="Invalid dice sides"):
            self.parser.parse("3d0")
        
        # No valid dice notation
        with pytest.raises(ValueError, match="No valid dice notation"):
            self.parser.parse("abc")
        
        # Keep more than rolled
        with pytest.raises(ValueError, match="Cannot keep 5 dice from 3 rolled"):
            self.parser.parse("3d6kh5")
        
        # Drop all dice
        with pytest.raises(ValueError, match="Cannot drop 3 dice from 3 rolled"):
            self.parser.parse("3d6dl3")
    
    def test_string_representation(self):
        """Test string representation of parsed expressions."""
        tests = [
            ("d20", "1d20"),
            ("3d6+2", "3d6+2"),
            ("2d10-1", "2d10-1"),
            ("4d6kh3", "4d6kh3"),
            ("4d6dl1", "4d6dl1"),
        ]
        
        for input_str, expected in tests:
            expr = self.parser.parse(input_str)
            assert str(expr) == expected