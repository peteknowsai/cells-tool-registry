#!/usr/bin/env python3
"""
Tests for current-time CLI tool
"""

import json
import subprocess
import sys
from datetime import datetime
import os


# Path to the current_time.py script
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "current_time.py")


def run_command(args):
    """Run the current-time command with given arguments."""
    cmd = [sys.executable, SCRIPT_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


class TestBasicFunctionality:
    """Test basic command functionality."""
    
    def test_help_command(self):
        """Test --help flag."""
        result = run_command(["--help"])
        assert result.returncode == 0
        assert "Display current time" in result.stdout
        assert "Examples:" in result.stdout
    
    def test_default_command(self):
        """Test running without arguments shows local time."""
        result = run_command([])
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
        # Should contain day name for human format
        assert any(day in result.stdout for day in 
                  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    
    def test_utc_flag(self):
        """Test --utc flag."""
        result = run_command(["--utc"])
        assert result.returncode == 0
        assert "UTC" in result.stdout or "Coordinated Universal Time" in result.stdout
    
    def test_specific_timezone(self):
        """Test --tz with specific timezone."""
        result = run_command(["--tz", "America/New_York"])
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
    
    def test_invalid_timezone(self):
        """Test with invalid timezone."""
        result = run_command(["--tz", "Invalid/Timezone"])
        assert result.returncode == 1
        assert "Error" in result.stderr
        # Should suggest similar timezones
        assert "Did you mean" in result.stderr or "Invalid timezone" in result.stderr


class TestFormats:
    """Test different output formats."""
    
    def test_iso_format(self):
        """Test ISO 8601 format."""
        result = run_command(["--format", "iso", "--utc"])
        assert result.returncode == 0
        output = result.stdout.strip()
        # ISO format should contain T and timezone info
        assert "T" in output
        assert "+" in output or "Z" in output
    
    def test_rfc3339_format(self):
        """Test RFC 3339 format."""
        result = run_command(["--format", "rfc3339", "--utc"])
        assert result.returncode == 0
        output = result.stdout.strip()
        # Should end with Z for UTC
        assert output.endswith("Z")
    
    def test_unix_format(self):
        """Test Unix timestamp format."""
        result = run_command(["--format", "unix"])
        assert result.returncode == 0
        output = result.stdout.strip()
        # Should be a number
        assert output.isdigit()
        # Should be a reasonable timestamp (after year 2020)
        assert int(output) > 1577836800
    
    def test_custom_format(self):
        """Test custom strftime format."""
        result = run_command(["--format", "custom", "--custom-format", "%Y-%m-%d"])
        assert result.returncode == 0
        output = result.stdout.strip()
        # Should match YYYY-MM-DD format
        assert len(output) == 10
        assert output[4] == "-" and output[7] == "-"


class TestMultipleTimezones:
    """Test multiple timezone display."""
    
    def test_zones_list(self):
        """Test --zones with comma-separated list."""
        result = run_command(["--zones", "UTC,America/New_York,Asia/Tokyo"])
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 3
        assert "UTC" in lines[0]
        assert "America/New_York" in lines[1]
        assert "Asia/Tokyo" in lines[2]
    
    def test_all_zones(self):
        """Test --all-zones flag."""
        result = run_command(["--all-zones"])
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        # Should show multiple major timezones
        assert len(lines) >= 10
        assert any("UTC" in line for line in lines)
        assert any("America/New_York" in line for line in lines)


class TestJSONOutput:
    """Test JSON output functionality."""
    
    def test_json_single_timezone(self):
        """Test JSON output for single timezone."""
        result = run_command(["--json", "--utc"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "timezone" in data
        assert "time" in data
        assert "format" in data
        assert data["timezone"] == "UTC"
    
    def test_json_multiple_timezones(self):
        """Test JSON output for multiple timezones."""
        result = run_command(["--json", "--zones", "UTC,America/New_York"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "times" in data
        assert len(data["times"]) == 2
        assert data["times"][0]["timezone"] == "UTC"
        assert data["times"][1]["timezone"] == "America/New_York"
    
    def test_json_verbose(self):
        """Test JSON output with verbose flag."""
        result = run_command(["--json", "--verbose", "--utc"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "utc_offset" in data
        assert "week_number" in data
        assert "day_of_year" in data


class TestListZonesCommand:
    """Test list-zones subcommand."""
    
    def test_list_all_zones(self):
        """Test listing all timezones."""
        result = run_command(["list-zones"])
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        # Should have many timezones
        assert len(lines) > 100
        assert "Total:" in lines[-1]
    
    def test_list_zones_filter(self):
        """Test filtering timezones."""
        result = run_command(["list-zones", "--filter", "America"])
        assert result.returncode == 0
        lines = result.stdout.strip().split("\n")
        # All lines except the last should contain "America"
        for line in lines[:-1]:
            assert "America" in line
    
    def test_list_zones_json(self):
        """Test list-zones with JSON output."""
        result = run_command(["list-zones", "--json", "--filter", "Europe"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "timezones" in data
        assert "count" in data
        assert data["count"] == len(data["timezones"])
        # All timezones should contain "Europe"
        for tz in data["timezones"]:
            assert "Europe" in tz


class TestConvertCommand:
    """Test convert subcommand."""
    
    def test_convert_basic(self):
        """Test basic time conversion."""
        result = run_command(["convert", "2024-06-14 10:30", "--from", "UTC", "--to", "America/New_York"])
        assert result.returncode == 0
        assert "06:30" in result.stdout  # UTC 10:30 is 06:30 EDT
    
    def test_convert_json(self):
        """Test convert with JSON output."""
        result = run_command(["convert", "2024-06-14 10:30", "--from", "UTC", "--to", "Asia/Tokyo", "--json"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["input_time"] == "2024-06-14 10:30"
        assert data["from_timezone"] == "UTC"
        assert data["to_timezone"] == "Asia/Tokyo"
        assert "19:30" in data["converted_time"]  # UTC 10:30 is 19:30 JST
    
    def test_convert_invalid_time(self):
        """Test convert with invalid time format."""
        result = run_command(["convert", "invalid-time", "--from", "UTC", "--to", "UTC"])
        assert result.returncode == 1
        assert "Unable to parse time" in result.stderr
    
    def test_convert_invalid_timezone(self):
        """Test convert with invalid timezone."""
        result = run_command(["convert", "2024-06-14 10:30", "--from", "Invalid/Zone", "--to", "UTC"])
        assert result.returncode == 1
        assert "Error" in result.stderr


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_custom_format_without_string(self):
        """Test using custom format without providing format string."""
        result = run_command(["--format", "custom"])
        # Should still work, just use default format
        assert result.returncode == 0
    
    def test_mixed_invalid_valid_timezones(self):
        """Test mixing valid and invalid timezones."""
        result = run_command(["--zones", "UTC,Invalid/Zone,America/New_York"])
        # Should still show valid timezones
        assert "UTC" in result.stdout
        assert "America/New_York" in result.stdout
        assert "Error" in result.stderr


if __name__ == "__main__":
    # Run a quick smoke test
    print("Running smoke test...")
    result = run_command(["--help"])
    if result.returncode == 0:
        print("✓ Help command works")
    
    result = run_command(["--utc", "--format", "iso"])
    if result.returncode == 0:
        print("✓ Basic functionality works")
        print(f"  Current UTC time (ISO): {result.stdout.strip()}")
    
    print("\nRun 'pytest' for full test suite")