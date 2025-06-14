#!/usr/bin/env python3
"""
Current-Time CLI Tool

A command-line tool for displaying current time in various formats and timezones.
"""

import argparse
import json
import sys
from datetime import datetime
from functools import lru_cache
from typing import List, Optional, Dict, Any

try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError:
    # Fallback for Python < 3.9
    try:
        import pytz
        ZoneInfo = pytz.timezone
        available_timezones = pytz.all_timezones
    except ImportError:
        print("Error: Neither zoneinfo nor pytz is available.", file=sys.stderr)
        print("Install pytz with: pip install pytz", file=sys.stderr)
        sys.exit(1)


# Common timezone groups
MAJOR_TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Chicago", 
    "America/Denver",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
]


@lru_cache(maxsize=None)
def get_all_timezones() -> List[str]:
    """Get all available timezones (cached for performance)."""
    if hasattr(available_timezones, '__call__'):
        return sorted(available_timezones())
    return sorted(available_timezones)


def format_time_iso(dt: datetime) -> str:
    """Format datetime as ISO 8601."""
    return dt.isoformat()


def format_time_rfc3339(dt: datetime) -> str:
    """Format datetime as RFC 3339."""
    if dt.tzinfo and dt.utcoffset() == datetime.now(ZoneInfo("UTC")).utcoffset():
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return dt.isoformat()


def format_time_unix(dt: datetime) -> str:
    """Format datetime as Unix timestamp."""
    return str(int(dt.timestamp()))


def format_time_human(dt: datetime) -> str:
    """Format datetime in human-readable format."""
    return dt.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")


def format_time_custom(dt: datetime, fmt: str) -> str:
    """Format datetime with custom strftime format."""
    return dt.strftime(fmt)


def get_timezone_time(timezone: str) -> datetime:
    """Get current time in specified timezone."""
    try:
        return datetime.now(ZoneInfo(timezone))
    except Exception as e:
        raise ValueError(f"Invalid timezone '{timezone}': {e}")


def find_similar_timezones(query: str, limit: int = 5) -> List[str]:
    """Find timezones similar to the query."""
    query_lower = query.lower()
    all_tz = get_all_timezones()
    
    # Exact matches first
    exact = [tz for tz in all_tz if query_lower == tz.lower()]
    if exact:
        return exact[:limit]
    
    # Partial matches
    partial = [tz for tz in all_tz if query_lower in tz.lower()]
    return partial[:limit]


def convert_time(time_str: str, from_tz: str, to_tz: str) -> datetime:
    """Convert time from one timezone to another."""
    # Parse the input time
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
    ]
    
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            continue
    
    if dt is None:
        raise ValueError(f"Unable to parse time '{time_str}'. Use format: YYYY-MM-DD HH:MM:SS")
    
    # Add timezone info
    from_zone = ZoneInfo(from_tz)
    dt = dt.replace(tzinfo=from_zone)
    
    # Convert to target timezone
    to_zone = ZoneInfo(to_tz)
    return dt.astimezone(to_zone)


def display_single_time(timezone: Optional[str], format_type: str, custom_format: Optional[str], 
                       use_json: bool, verbose: bool) -> Dict[str, Any]:
    """Display time for a single timezone."""
    # Get the time
    if timezone:
        dt = get_timezone_time(timezone)
        display_tz = timezone
    else:
        dt = datetime.now().astimezone()
        display_tz = dt.tzinfo.tzname(dt) or "Local"
    
    # Format the time
    if format_type == "iso":
        formatted = format_time_iso(dt)
    elif format_type == "rfc3339":
        formatted = format_time_rfc3339(dt)
    elif format_type == "unix":
        formatted = format_time_unix(dt)
    elif format_type == "custom" and custom_format:
        formatted = format_time_custom(dt, custom_format)
    else:  # human
        formatted = format_time_human(dt)
    
    result = {
        "timezone": display_tz,
        "time": formatted,
        "format": format_type,
    }
    
    if verbose:
        result.update({
            "utc_offset": dt.strftime("%z"),
            "timezone_abbr": dt.strftime("%Z"),
            "week_number": dt.isocalendar()[1],
            "day_of_year": dt.timetuple().tm_yday,
        })
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Display current time in various formats and timezones",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  current-time                              # Show local time
  current-time --utc                        # Show UTC time
  current-time --tz "America/New_York"      # Show time in New York
  current-time --format iso                 # Use ISO 8601 format
  current-time --zones "UTC,Asia/Tokyo"     # Show multiple timezones
  current-time list-zones                   # List all timezones
  current-time convert "2024-06-14 10:30" --from UTC --to "Asia/Tokyo"
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List zones command
    list_parser = subparsers.add_parser("list-zones", help="List available timezones")
    list_parser.add_argument("--filter", help="Filter timezones by keyword")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert time between timezones")
    convert_parser.add_argument("time", help="Time to convert (YYYY-MM-DD HH:MM:SS)")
    convert_parser.add_argument("--from", dest="from_tz", required=True, help="Source timezone")
    convert_parser.add_argument("--to", dest="to_tz", required=True, help="Target timezone")
    convert_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Main command options
    parser.add_argument("--tz", "--timezone", dest="timezone", help="Display time in specific timezone")
    parser.add_argument("--utc", action="store_true", help="Display UTC time")
    parser.add_argument("--zones", help="Comma-separated list of timezones to display")
    parser.add_argument("--all-zones", action="store_true", help="Display time in all major timezones")
    parser.add_argument("--format", choices=["iso", "rfc3339", "unix", "human", "custom"], 
                       default="human", help="Output format")
    parser.add_argument("--custom-format", help="Custom strftime format string")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Include additional information")
    
    args = parser.parse_args()
    
    try:
        # Handle subcommands
        if args.command == "list-zones":
            zones = get_all_timezones()
            if args.filter:
                zones = [z for z in zones if args.filter.lower() in z.lower()]
            
            if args.json:
                print(json.dumps({"timezones": zones, "count": len(zones)}, indent=2))
            else:
                for zone in zones:
                    print(zone)
                print(f"\nTotal: {len(zones)} timezones")
            return
        
        elif args.command == "convert":
            try:
                converted = convert_time(args.time, args.from_tz, args.to_tz)
                result = {
                    "input_time": args.time,
                    "from_timezone": args.from_tz,
                    "to_timezone": args.to_tz,
                    "converted_time": converted.strftime("%Y-%m-%d %H:%M:%S %Z"),
                }
                
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"{args.time} {args.from_tz} → {result['converted_time']}")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                
                # Suggest similar timezones
                for tz in [args.from_tz, args.to_tz]:
                    if tz not in get_all_timezones():
                        similar = find_similar_timezones(tz)
                        if similar:
                            print(f"\nDid you mean one of these timezones instead of '{tz}'?", file=sys.stderr)
                            for s in similar:
                                print(f"  - {s}", file=sys.stderr)
                sys.exit(1)
            return
        
        # Handle main display command
        timezones = []
        
        if args.all_zones:
            timezones = MAJOR_TIMEZONES
        elif args.zones:
            timezones = [z.strip() for z in args.zones.split(",")]
        elif args.utc:
            timezones = ["UTC"]
        elif args.timezone:
            timezones = [args.timezone]
        else:
            timezones = [None]  # Local time
        
        # Display times
        results = []
        for tz in timezones:
            try:
                result = display_single_time(tz, args.format, args.custom_format, 
                                           args.json, args.verbose)
                results.append(result)
                
                if not args.json:
                    if len(timezones) > 1:
                        print(f"{result['timezone']:<20} {result['time']}")
                    else:
                        print(result['time'])
                        
            except ValueError as e:
                if args.json:
                    results.append({"timezone": tz, "error": str(e)})
                else:
                    print(f"Error with timezone '{tz}': {e}", file=sys.stderr)
                    
                    # Suggest similar timezones
                    if tz and tz not in get_all_timezones():
                        similar = find_similar_timezones(tz)
                        if similar:
                            print(f"\nDid you mean one of these?", file=sys.stderr)
                            for s in similar:
                                print(f"  - {s}", file=sys.stderr)
        
        if args.json:
            if len(results) == 1:
                print(json.dumps(results[0], indent=2))
            else:
                print(json.dumps({"times": results}, indent=2))
    
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()