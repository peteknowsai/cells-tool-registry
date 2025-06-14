#!/usr/bin/env python3
"""
Weather CLI - A command-line weather tool using OpenWeatherMap API
"""

import argparse
import json
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import time

try:
    from pyowm import OWM
    from pyowm.commons.exceptions import APIRequestError, APIResponseError, NotFoundError
except ImportError:
    print("Error: pyowm is not installed. Please run: pip install pyowm")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Error: rich is not installed. Please run: pip install rich")
    sys.exit(1)


class ConfigManager:
    """Manages API key configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".weather-cli"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment or config file"""
        # First check environment variable
        api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
        if api_key:
            return api_key
        
        # Then check config file
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    return config.get("api_key")
            except (json.JSONDecodeError, IOError):
                return None
        
        return None
    
    def set_api_key(self, api_key: str) -> None:
        """Save API key to config file"""
        config = {"api_key": api_key}
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        os.chmod(self.config_file, 0o600)  # Secure file permissions
    
    def show_config(self) -> Dict:
        """Show current configuration"""
        api_key = self.get_api_key()
        return {
            "api_key_configured": bool(api_key),
            "api_key_source": "environment" if os.environ.get("OPENWEATHERMAP_API_KEY") else "config_file",
            "config_path": str(self.config_file)
        }


class CacheManager:
    """Manages weather data caching"""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".weather-cli"
        self.cache_file = self.cache_dir / "cache.db"
        self.cache_dir.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.cache_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT,
                timestamp REAL
            )
        """)
        conn.commit()
        conn.close()
    
    def _generate_key(self, location: str, units: str, data_type: str) -> str:
        """Generate cache key"""
        # Round timestamp to 5-minute bucket
        timestamp = int(time.time() // 300) * 300
        return f"{location}_{units}_{data_type}_{timestamp}"
    
    def get(self, location: str, units: str, data_type: str) -> Optional[Dict]:
        """Get cached data if valid"""
        cache_key = self._generate_key(location, units, data_type)
        
        conn = sqlite3.connect(self.cache_file)
        cursor = conn.execute(
            "SELECT data, timestamp FROM weather_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data, timestamp = row
            # Check if cache is still valid (5 minutes)
            if time.time() - timestamp < 300:
                return json.loads(data)
        
        return None
    
    def set(self, location: str, units: str, data_type: str, data: Dict) -> None:
        """Cache weather data"""
        cache_key = self._generate_key(location, units, data_type)
        
        conn = sqlite3.connect(self.cache_file)
        conn.execute(
            "INSERT OR REPLACE INTO weather_cache (cache_key, data, timestamp) VALUES (?, ?, ?)",
            (cache_key, json.dumps(data), time.time())
        )
        conn.commit()
        conn.close()
    
    def clear_expired(self) -> None:
        """Clear expired cache entries"""
        conn = sqlite3.connect(self.cache_file)
        conn.execute(
            "DELETE FROM weather_cache WHERE timestamp < ?",
            (time.time() - 300,)
        )
        conn.commit()
        conn.close()


class WeatherService:
    """Handles OpenWeatherMap API interactions"""
    
    def __init__(self, api_key: str, cache_manager: CacheManager):
        self.owm = OWM(api_key)
        self.mgr = self.owm.weather_manager()
        self.cache = cache_manager
    
    def get_current_weather(self, location: str, units: str = "metric", use_cache: bool = True) -> Dict:
        """Get current weather for a location"""
        # Check cache first
        if use_cache:
            cached = self.cache.get(location, units, "current")
            if cached:
                cached["from_cache"] = True
                return cached
        
        try:
            # Try to parse as coordinates
            if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
                lat, lon = map(float, location.split(","))
                observation = self.mgr.weather_at_coords(lat, lon)
            else:
                # Use as city name
                observation = self.mgr.weather_at_place(location)
            
            weather = observation.weather
            
            # Convert units
            temp_unit = "celsius" if units == "metric" else "fahrenheit"
            wind_unit = "meters_sec" if units == "metric" else "miles_hour"
            
            data = {
                "location": {
                    "name": observation.location.name,
                    "country": observation.location.country,
                    "coordinates": {
                        "lat": observation.location.lat,
                        "lon": observation.location.lon
                    }
                },
                "current": {
                    "temperature": round(weather.temperature(temp_unit)["temp"], 1),
                    "feels_like": round(weather.temperature(temp_unit)["feels_like"], 1),
                    "temp_min": round(weather.temperature(temp_unit)["temp_min"], 1),
                    "temp_max": round(weather.temperature(temp_unit)["temp_max"], 1),
                    "condition": weather.detailed_status.capitalize(),
                    "humidity": weather.humidity,
                    "pressure": weather.pressure["press"],
                    "wind": {
                        "speed": round(weather.wind(unit=wind_unit)["speed"], 1),
                        "direction": self._get_wind_direction(weather.wind().get("deg", 0))
                    },
                    "clouds": weather.clouds,
                    "visibility": weather.visibility_distance if hasattr(weather, 'visibility_distance') else None,
                    "timestamp": weather.reference_time("iso"),
                    "sunrise": weather.sunrise_time("iso") if weather.sunrise_time else None,
                    "sunset": weather.sunset_time("iso") if weather.sunset_time else None
                },
                "units": {
                    "temperature": "°C" if units == "metric" else "°F",
                    "wind": "m/s" if units == "metric" else "mph"
                },
                "from_cache": False
            }
            
            # Cache the result
            self.cache.set(location, units, "current", data)
            
            return data
            
        except NotFoundError:
            raise ValueError(f"Location '{location}' not found. Try using coordinates or adding country code (e.g., 'London,GB')")
        except APIRequestError as e:
            raise RuntimeError(f"API request failed: {str(e)}")
    
    def get_forecast(self, location: str, days: int = 3, units: str = "metric", use_cache: bool = True) -> Dict:
        """Get weather forecast for a location"""
        # Check cache first
        if use_cache:
            cached = self.cache.get(location, units, f"forecast_{days}")
            if cached:
                cached["from_cache"] = True
                return cached
        
        try:
            # Try to parse as coordinates
            if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
                lat, lon = map(float, location.split(","))
                forecast = self.mgr.forecast_at_coords(lat, lon, "3h")
            else:
                # Use as city name
                forecast = self.mgr.forecast_at_place(location, "3h")
            
            # Convert units
            temp_unit = "celsius" if units == "metric" else "fahrenheit"
            wind_unit = "meters_sec" if units == "metric" else "miles_hour"
            
            # Group forecasts by day
            daily_forecasts = {}
            for weather in forecast.forecast:
                date = weather.reference_time("date").date()
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(weather)
            
            # Build forecast data
            forecast_data = []
            for date, weathers in sorted(daily_forecasts.items())[:days]:
                # Calculate daily aggregates
                temps = [w.temperature(temp_unit)["temp"] for w in weathers]
                conditions = [w.detailed_status for w in weathers]
                
                # Find most common condition
                condition_counts = {}
                for cond in conditions:
                    condition_counts[cond] = condition_counts.get(cond, 0) + 1
                main_condition = max(condition_counts, key=condition_counts.get)
                
                forecast_data.append({
                    "date": date.isoformat(),
                    "temperature": {
                        "min": round(min(temps), 1),
                        "max": round(max(temps), 1),
                        "avg": round(sum(temps) / len(temps), 1)
                    },
                    "condition": main_condition.capitalize(),
                    "humidity": round(sum(w.humidity for w in weathers) / len(weathers)),
                    "wind": {
                        "speed": round(sum(w.wind(unit=wind_unit)["speed"] for w in weathers) / len(weathers), 1),
                        "direction": self._get_wind_direction(weathers[0].wind().get("deg", 0))
                    }
                })
            
            data = {
                "location": {
                    "name": forecast.location.name,
                    "country": forecast.location.country,
                    "coordinates": {
                        "lat": forecast.location.lat,
                        "lon": forecast.location.lon
                    }
                },
                "forecast": forecast_data,
                "units": {
                    "temperature": "°C" if units == "metric" else "°F",
                    "wind": "m/s" if units == "metric" else "mph"
                },
                "from_cache": False
            }
            
            # Cache the result
            self.cache.set(location, units, f"forecast_{days}", data)
            
            return data
            
        except NotFoundError:
            raise ValueError(f"Location '{location}' not found. Try using coordinates or adding country code (e.g., 'London,GB')")
        except APIRequestError as e:
            raise RuntimeError(f"API request failed: {str(e)}")
    
    def _get_wind_direction(self, degrees: int) -> str:
        """Convert wind degrees to cardinal direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]


class WeatherFormatter:
    """Formats weather data for display"""
    
    def __init__(self):
        self.console = Console()
    
    def format_current_weather(self, data: Dict, json_output: bool = False) -> None:
        """Format and display current weather"""
        if json_output:
            print(json.dumps(data, indent=2))
            return
        
        location = data["location"]
        current = data["current"]
        units = data["units"]
        
        # Create weather panel
        content = []
        content.append(f"[bold cyan]Temperature:[/] {current['temperature']}{units['temperature']} (feels like {current['feels_like']}{units['temperature']})")
        content.append(f"[bold cyan]Min/Max:[/] {current['temp_min']}{units['temperature']} / {current['temp_max']}{units['temperature']}")
        content.append(f"[bold yellow]Condition:[/] {current['condition']}")
        content.append(f"[bold blue]Humidity:[/] {current['humidity']}%")
        content.append(f"[bold green]Wind:[/] {current['wind']['speed']} {units['wind']} {current['wind']['direction']}")
        content.append(f"[bold magenta]Pressure:[/] {current['pressure']} hPa")
        content.append(f"[bold cyan]Clouds:[/] {current['clouds']}%")
        
        if current.get('visibility'):
            content.append(f"[bold white]Visibility:[/] {current['visibility']} m")
        
        if current.get('sunrise') and current.get('sunset'):
            sunrise = datetime.fromisoformat(current['sunrise'].replace('Z', '+00:00')).strftime("%H:%M")
            sunset = datetime.fromisoformat(current['sunset'].replace('Z', '+00:00')).strftime("%H:%M")
            content.append(f"[bold yellow]Sunrise/Sunset:[/] {sunrise} / {sunset}")
        
        timestamp = datetime.fromisoformat(current['timestamp'].replace('Z', '+00:00'))
        content.append(f"\n[dim]Updated: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}[/]")
        
        if data.get("from_cache"):
            content.append("[dim](from cache)[/]")
        
        panel = Panel(
            "\n".join(content),
            title=f"Current Weather for {location['name']}, {location['country']}",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def format_forecast(self, data: Dict, json_output: bool = False) -> None:
        """Format and display weather forecast"""
        if json_output:
            print(json.dumps(data, indent=2))
            return
        
        location = data["location"]
        units = data["units"]
        
        # Create forecast table
        table = Table(
            title=f"Weather Forecast for {location['name']}, {location['country']}",
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Temperature", style="yellow", width=20)
        table.add_column("Condition", style="green", width=20)
        table.add_column("Humidity", style="blue", width=10)
        table.add_column("Wind", style="magenta", width=15)
        
        for day in data["forecast"]:
            date = datetime.fromisoformat(day["date"])
            date_str = date.strftime("%a %b %d")
            
            temp_str = f"{day['temperature']['min']}-{day['temperature']['max']}{units['temperature']} (avg: {day['temperature']['avg']}{units['temperature']})"
            wind_str = f"{day['wind']['speed']} {units['wind']} {day['wind']['direction']}"
            
            table.add_row(
                date_str,
                temp_str,
                day["condition"],
                f"{day['humidity']}%",
                wind_str
            )
        
        if data.get("from_cache"):
            table.caption = "[dim](from cache)[/]"
        
        self.console.print(table)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Weather CLI - Get weather information from OpenWeatherMap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  weather-cli current --city London
  weather-cli current --coords 51.5074,-0.1278 --units imperial
  weather-cli forecast --city "New York,US" --days 5
  weather-cli config --set-key YOUR_API_KEY
        """
    )
    
    parser.add_argument("--version", "-v", action="version", version="weather-cli 1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Current weather command
    current_parser = subparsers.add_parser("current", help="Get current weather")
    location_group = current_parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument("--city", "-c", help="City name (e.g., 'London' or 'London,GB')")
    location_group.add_argument("--coords", help="Coordinates as 'lat,lon' (e.g., '51.5074,-0.1278')")
    current_parser.add_argument("--units", "-u", choices=["metric", "imperial"], default="metric", help="Temperature units")
    current_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    current_parser.add_argument("--no-cache", action="store_true", help="Bypass cache")
    
    # Forecast command
    forecast_parser = subparsers.add_parser("forecast", help="Get weather forecast")
    location_group = forecast_parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument("--city", "-c", help="City name (e.g., 'London' or 'London,GB')")
    location_group.add_argument("--coords", help="Coordinates as 'lat,lon' (e.g., '51.5074,-0.1278')")
    forecast_parser.add_argument("--days", "-d", type=int, choices=range(1, 6), default=3, help="Number of days (1-5)")
    forecast_parser.add_argument("--units", "-u", choices=["metric", "imperial"], default="metric", help="Temperature units")
    forecast_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    forecast_parser.add_argument("--no-cache", action="store_true", help="Bypass cache")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure weather-cli")
    config_parser.add_argument("--set-key", metavar="API_KEY", help="Set OpenWeatherMap API key")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize components
    config_mgr = ConfigManager()
    cache_mgr = CacheManager()
    formatter = WeatherFormatter()
    
    try:
        if args.command == "config":
            if args.set_key:
                config_mgr.set_api_key(args.set_key)
                print("✓ API key saved successfully!")
                print("You can now use weather-cli commands.")
            elif args.show:
                config = config_mgr.show_config()
                print(json.dumps(config, indent=2))
            else:
                config_parser.print_help()
        
        else:
            # Get API key
            api_key = config_mgr.get_api_key()
            if not api_key:
                print("Error: No API key configured!")
                print("\nTo get started:")
                print("1. Sign up at https://openweathermap.org/api")
                print("2. Get your API key from the account page")
                print("3. Configure weather-cli with: weather-cli config --set-key YOUR_API_KEY")
                print("\nAlternatively, set the OPENWEATHERMAP_API_KEY environment variable.")
                sys.exit(1)
            
            # Initialize weather service
            weather_service = WeatherService(api_key, cache_mgr)
            
            # Clear expired cache entries periodically
            cache_mgr.clear_expired()
            
            if args.command == "current":
                location = args.city or args.coords
                data = weather_service.get_current_weather(
                    location, 
                    units=args.units,
                    use_cache=not args.no_cache
                )
                formatter.format_current_weather(data, json_output=args.json)
            
            elif args.command == "forecast":
                location = args.city or args.coords
                data = weather_service.get_forecast(
                    location,
                    days=args.days,
                    units=args.units,
                    use_cache=not args.no_cache
                )
                formatter.format_forecast(data, json_output=args.json)
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()