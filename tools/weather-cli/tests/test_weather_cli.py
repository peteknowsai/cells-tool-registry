#!/usr/bin/env python3
"""Tests for Weather CLI"""

import os
import sys
import json
import pytest
import sqlite3
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weather_cli
from weather_cli import ConfigManager, CacheManager, WeatherService, WeatherFormatter


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    def test_get_api_key_from_env(self):
        """Test getting API key from environment"""
        with patch.dict(os.environ, {'OPENWEATHERMAP_API_KEY': 'test_key'}):
            with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
                config = ConfigManager()
                assert config.get_api_key() == 'test_key'
    
    def test_get_api_key_from_file(self):
        """Test getting API key from config file"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
                config = ConfigManager()
                config.set_api_key('file_key')
                assert config.get_api_key() == 'file_key'
    
    def test_set_api_key(self):
        """Test setting API key"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            config = ConfigManager()
            config.set_api_key('new_key')
            
            # Read back from file
            with open(config.config_file, 'r') as f:
                saved_config = json.load(f)
            assert saved_config['api_key'] == 'new_key'
    
    def test_show_config(self):
        """Test showing configuration"""
        with patch.dict(os.environ, {'OPENWEATHERMAP_API_KEY': 'env_key'}):
            with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
                config = ConfigManager()
                info = config.show_config()
                assert info['api_key_configured'] is True
                assert info['api_key_source'] == 'environment'


class TestCacheManager:
    """Test CacheManager functionality"""
    
    def test_cache_operations(self):
        """Test cache get and set operations"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            # Test set
            test_data = {'temperature': 20.5, 'condition': 'Clear'}
            cache.set('London', 'metric', 'current', test_data)
            
            # Test get (should return cached data)
            cached = cache.get('London', 'metric', 'current')
            assert cached is not None
            assert cached['temperature'] == 20.5
            assert cached['condition'] == 'Clear'
    
    def test_cache_expiry(self):
        """Test cache expiry"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            # Set data with old timestamp
            test_data = {'temperature': 20.5}
            cache_key = cache._generate_key('London', 'metric', 'current')
            
            conn = sqlite3.connect(cache.cache_file)
            conn.execute(
                "INSERT INTO weather_cache (cache_key, data, timestamp) VALUES (?, ?, ?)",
                (cache_key, json.dumps(test_data), 0)  # Very old timestamp
            )
            conn.commit()
            conn.close()
            
            # Should return None due to expiry
            cached = cache.get('London', 'metric', 'current')
            assert cached is None


class TestWeatherService:
    """Test WeatherService functionality"""
    
    @pytest.fixture
    def mock_weather(self):
        """Create a mock weather object"""
        weather = Mock()
        weather.reference_time.return_value = '2024-01-01T12:00:00Z'
        weather.detailed_status = 'clear sky'
        weather.temperature.return_value = {
            'temp': 20.5,
            'feels_like': 19.0,
            'temp_min': 18.0,
            'temp_max': 22.0
        }
        weather.humidity = 65
        weather.pressure = {'press': 1013}
        weather.wind.return_value = {'speed': 3.5, 'deg': 180}
        weather.clouds = 10
        weather.visibility_distance = 10000
        weather.sunrise_time = lambda fmt: '2024-01-01T06:00:00Z' if fmt == 'iso' else None
        weather.sunset_time = lambda fmt: '2024-01-01T18:00:00Z' if fmt == 'iso' else None
        return weather
    
    @pytest.fixture
    def mock_location(self):
        """Create a mock location object"""
        location = Mock()
        location.name = 'London'
        location.country = 'GB'
        location.lat = 51.5074
        location.lon = -0.1278
        return location
    
    @pytest.fixture
    def mock_observation(self, mock_weather, mock_location):
        """Create a mock observation object"""
        observation = Mock()
        observation.weather = mock_weather
        observation.location = mock_location
        return observation
    
    def test_get_current_weather(self, mock_observation):
        """Test getting current weather"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            with patch('weather_cli.OWM') as mock_owm_class:
                mock_owm = Mock()
                mock_mgr = Mock()
                mock_mgr.weather_at_place.return_value = mock_observation
                mock_owm.weather_manager.return_value = mock_mgr
                mock_owm_class.return_value = mock_owm
                
                service = WeatherService('test_key', cache)
                data = service.get_current_weather('London', 'metric', use_cache=False)
                
                assert data['location']['name'] == 'London'
                assert data['location']['country'] == 'GB'
                assert data['current']['temperature'] == 20.5
                assert data['current']['humidity'] == 65
                assert data['current']['condition'] == 'Clear sky'
    
    def test_get_current_weather_coordinates(self, mock_observation):
        """Test getting weather by coordinates"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            with patch('weather_cli.OWM') as mock_owm_class:
                mock_owm = Mock()
                mock_mgr = Mock()
                mock_mgr.weather_at_coords.return_value = mock_observation
                mock_owm.weather_manager.return_value = mock_mgr
                mock_owm_class.return_value = mock_owm
                
                service = WeatherService('test_key', cache)
                data = service.get_current_weather('51.5074,-0.1278', 'metric', use_cache=False)
                
                mock_mgr.weather_at_coords.assert_called_once_with(51.5074, -0.1278)
                assert data['location']['name'] == 'London'
    
    def test_get_current_weather_not_found(self):
        """Test handling location not found"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            with patch('weather_cli.OWM') as mock_owm_class:
                from pyowm.commons.exceptions import NotFoundError
                
                mock_owm = Mock()
                mock_mgr = Mock()
                mock_mgr.weather_at_place.side_effect = NotFoundError('Not found')
                mock_owm.weather_manager.return_value = mock_mgr
                mock_owm_class.return_value = mock_owm
                
                service = WeatherService('test_key', cache)
                
                with pytest.raises(ValueError) as exc_info:
                    service.get_current_weather('InvalidCity', 'metric', use_cache=False)
                
                assert "not found" in str(exc_info.value)
    
    def test_wind_direction(self):
        """Test wind direction conversion"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            cache = CacheManager()
            
            with patch('weather_cli.OWM'):
                service = WeatherService('test_key', cache)
                
                assert service._get_wind_direction(0) == 'N'
                assert service._get_wind_direction(45) == 'NE'
                assert service._get_wind_direction(90) == 'E'
                assert service._get_wind_direction(180) == 'S'
                assert service._get_wind_direction(270) == 'W'
                assert service._get_wind_direction(315) == 'NW'


class TestWeatherFormatter:
    """Test WeatherFormatter functionality"""
    
    def test_format_current_weather_json(self, capsys):
        """Test JSON output formatting"""
        formatter = WeatherFormatter()
        
        test_data = {
            'location': {'name': 'London', 'country': 'GB'},
            'current': {
                'temperature': 20.5,
                'feels_like': 19.0,
                'temp_min': 18.0,
                'temp_max': 22.0,
                'condition': 'Clear sky',
                'humidity': 65,
                'pressure': 1013,
                'wind': {'speed': 3.5, 'direction': 'S'},
                'clouds': 10,
                'timestamp': '2024-01-01T12:00:00Z'
            },
            'units': {'temperature': '°C', 'wind': 'm/s'}
        }
        
        formatter.format_current_weather(test_data, json_output=True)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['location']['name'] == 'London'
        assert output['current']['temperature'] == 20.5
    
    def test_format_forecast_json(self, capsys):
        """Test forecast JSON output"""
        formatter = WeatherFormatter()
        
        test_data = {
            'location': {'name': 'London', 'country': 'GB'},
            'forecast': [
                {
                    'date': '2024-01-01',
                    'temperature': {'min': 10.0, 'max': 15.0, 'avg': 12.5},
                    'condition': 'Partly cloudy',
                    'humidity': 70,
                    'wind': {'speed': 4.0, 'direction': 'W'}
                }
            ],
            'units': {'temperature': '°C', 'wind': 'm/s'}
        }
        
        formatter.format_forecast(test_data, json_output=True)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['forecast'][0]['temperature']['max'] == 15.0


class TestMainFunction:
    """Test main CLI function"""
    
    @patch('sys.argv', ['weather-cli'])
    def test_main_no_command(self):
        """Test main with no command"""
        with pytest.raises(SystemExit) as exc_info:
            weather_cli.main()
        assert exc_info.value.code == 1
    
    @patch('sys.argv', ['weather-cli', 'config', '--set-key', 'test_key'])
    def test_main_config_set_key(self, capsys):
        """Test setting API key via CLI"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            weather_cli.main()
            
            captured = capsys.readouterr()
            assert "API key saved successfully" in captured.out
    
    @patch('sys.argv', ['weather-cli', 'current', '--city', 'London'])
    def test_main_current_no_api_key(self):
        """Test current command without API key"""
        with patch('pathlib.Path.home', return_value=Path(tempfile.mkdtemp())):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(SystemExit) as exc_info:
                    weather_cli.main()
                assert exc_info.value.code == 1
    
    @patch('sys.argv', ['weather-cli', '--version'])
    def test_main_version(self, capsys):
        """Test version flag"""
        with pytest.raises(SystemExit) as exc_info:
            weather_cli.main()
        assert exc_info.value.code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])