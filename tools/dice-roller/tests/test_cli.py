#!/usr/bin/env python3
"""Tests for the CLI interface."""

import pytest
import subprocess
import json
import sys
import os

# Path to the dice roller script
SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dice_roller.py"
)


class TestCLI:
    """Test cases for CLI interface."""
    
    def run_command(self, args):
        """Run the dice roller command and return output."""
        cmd = [sys.executable, SCRIPT_PATH] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    
    def test_help(self):
        """Test help command."""
        code, stdout, stderr = self.run_command(["--help"])
        assert code == 0
        assert "Dice Roller" in stdout
        assert "positional arguments:" in stdout
    
    def test_roll_help(self):
        """Test roll command help."""
        code, stdout, stderr = self.run_command(["roll", "--help"])
        assert code == 0
        assert "usage: dice_roller.py roll" in stdout
        assert "--advantage" in stdout
    
    def test_simple_roll(self):
        """Test simple dice roll."""
        code, stdout, stderr = self.run_command(["roll", "d20"])
        assert code == 0
        assert "d20 = " in stdout
        # Check that result is between 1 and 20
        result = int(stdout.strip().split(" = ")[1])
        assert 1 <= result <= 20
    
    def test_roll_with_modifier(self):
        """Test roll with modifier."""
        code, stdout, stderr = self.run_command(["roll", "1d6+2"])
        assert code == 0
        assert "1d6+2 = " in stdout
        result = int(stdout.strip().split(" = ")[1])
        assert 3 <= result <= 8  # 1-6 + 2
    
    def test_show_rolls(self):
        """Test showing individual rolls."""
        code, stdout, stderr = self.run_command(["roll", "3d6", "--show-rolls"])
        assert code == 0
        assert "Rolling 3d6:" in stdout
        assert "3d6:" in stdout
        assert "Total:" in stdout
    
    def test_advantage(self):
        """Test advantage roll."""
        code, stdout, stderr = self.run_command(["roll", "--advantage", "--show-rolls"])
        assert code == 0
        assert "2d20kh1:" in stdout
        assert "kept:" in stdout
        assert "dropped:" in stdout
    
    def test_disadvantage(self):
        """Test disadvantage roll."""
        code, stdout, stderr = self.run_command(["roll", "--disadvantage", "--show-rolls"])
        assert code == 0
        assert "2d20dl1:" in stdout
    
    def test_repeat(self):
        """Test repeated rolls."""
        code, stdout, stderr = self.run_command(["roll", "d6", "--repeat", "3"])
        assert code == 0
        assert "Roll 1:" in stdout
        assert "Roll 2:" in stdout
        assert "Roll 3:" in stdout
    
    def test_json_output(self):
        """Test JSON output format."""
        code, stdout, stderr = self.run_command(["roll", "2d6+1", "--json"])
        assert code == 0
        
        data = json.loads(stdout)
        assert "rolls" in data
        assert "count" in data
        assert data["count"] == 1
        
        roll = data["rolls"][0]
        assert roll["expression"] == "2d6+1"
        assert roll["modifier"] == 1
        assert 3 <= roll["total"] <= 13
    
    def test_multiple_expressions(self):
        """Test multiple comma-separated expressions."""
        code, stdout, stderr = self.run_command(["roll", "d20,2d6+1"])
        assert code == 0
        lines = stdout.strip().split("\n")
        # Account for potential blank line
        assert len([l for l in lines if l]) == 2
        valid_lines = [l for l in lines if l]
        assert "d20 = " in valid_lines[0]
        assert "2d6+1 = " in valid_lines[1]
    
    def test_stats_command(self):
        """Test statistics command."""
        code, stdout, stderr = self.run_command(["stats", "3d6+2"])
        assert code == 0
        assert "Statistics for 3d6+2:" in stdout
        assert "Minimum: 5" in stdout  # 3*1 + 2
        assert "Maximum: 20" in stdout  # 3*6 + 2
        assert "Average:" in stdout
    
    def test_stats_json(self):
        """Test statistics JSON output."""
        code, stdout, stderr = self.run_command(["stats", "2d10", "--json"])
        assert code == 0
        
        data = json.loads(stdout)
        assert data["expression"] == "2d10"
        assert data["minimum"] == 2
        assert data["maximum"] == 20
        assert "average" in data
    
    def test_error_handling(self):
        """Test error handling."""
        # Invalid notation
        code, stdout, stderr = self.run_command(["roll", "invalid"])
        assert code == 1
        assert "Error:" in stderr
        
        # Both advantage and disadvantage
        code, stdout, stderr = self.run_command(["roll", "--advantage", "--disadvantage"])
        assert code == 1
        assert "Cannot use both" in stderr
        
        # Invalid dice
        code, stdout, stderr = self.run_command(["roll", "0d6"])
        assert code == 1
        assert "Invalid dice count" in stderr
    
    def test_keep_notation(self):
        """Test keep highest notation."""
        code, stdout, stderr = self.run_command(["roll", "4d6kh3", "--json"])
        assert code == 0
        
        data = json.loads(stdout)
        roll = data["rolls"][0]
        dice_result = roll["dice_results"][0]
        
        assert len(dice_result["rolls"]) == 4
        assert len(dice_result["kept_rolls"]) == 3
        assert len(dice_result["dropped_rolls"]) == 1