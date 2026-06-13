import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plugins_func.functions.get_weather import (
    get_weather_condition,
    fetch_weather_data,
    format_weather_report,
    get_weather
)


class TestWeatherPlugin(unittest.TestCase):
    """Test cases for the weather plugin functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conn = Mock()
        self.mock_conn.config = {
            "plugins": {
                "get_weather": {
                    "api_key": "test_api_key",
                    "default_location": "New York"
                }
            }
        }
        self.mock_conn.client_ip = "192.168.1.1"

    def test_get_weather_condition(self):
        """Test weather condition mapping."""
        # Test clear sky
        self.assertEqual(get_weather_condition("clear sky"), "Clear sky")
        
        # Test cloudy
        self.assertEqual(get_weather_condition("broken clouds"), "Broken clouds")
        
        # Test rain
        self.assertEqual(get_weather_condition("light rain"), "Light rain")
        
        # Test snow
        self.assertEqual(get_weather_condition("light snow"), "Light snow")
        
        # Test unknown condition
        self.assertEqual(get_weather_condition("unknown condition"), "Unknown Condition")

    @patch('plugins_func.functions.get_weather.requests.get')
    def test_fetch_weather_data_success(self, mock_get):
        """Test successful weather data fetching."""
        # Mock successful API responses
        current_response = Mock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {
                "temp": 20,
                "feels_like": 18,
                "humidity": 65,
                "pressure": 1013,
                "temp_min": 15,
                "temp_max": 25
            },
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.5, "deg": 180},
            "visibility": 10000
        }
        
        forecast_response = Mock()
        forecast_response.status_code = 200
        forecast_response.json.return_value = {
            "list": [
                {
                    "dt_txt": "2024-01-01 12:00:00",
                    "main": {"temp": 20, "humidity": 65},
                    "weather": [{"description": "clear sky"}],
                    "wind": {"speed": 3.5}
                }
            ]
        }
        
        mock_get.side_effect = [current_response, forecast_response]
        
        current_data, forecast_data = fetch_weather_data("New York", "test_key")
        
        self.assertIsNotNone(current_data)
        self.assertIsNotNone(forecast_data)
        self.assertEqual(current_data["name"], "New York")
        self.assertEqual(len(mock_get.call_args_list), 2)

    @patch('plugins_func.functions.get_weather.requests.get')
    def test_fetch_weather_data_api_error(self, mock_get):
        """Test weather data fetching with API error."""
        # Mock API error response
        error_response = Mock()
        error_response.status_code = 404
        error_response.text = "City not found"
        
        mock_get.return_value = error_response
        
        current_data, forecast_data = fetch_weather_data("InvalidCity", "test_key")
        
        self.assertIsNone(current_data)
        self.assertIsNone(forecast_data)

    def test_format_weather_report(self):
        """Test weather report formatting."""
        current_data = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {
                "temp": 20,
                "feels_like": 18,
                "humidity": 65,
                "pressure": 1013,
                "temp_min": 15,
                "temp_max": 25
            },
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.5, "deg": 180},
            "visibility": 10000
        }
        
        forecast_data = {
            "list": [
                {
                    "dt_txt": "2024-01-01 12:00:00",
                    "main": {"temp": 20, "humidity": 65},
                    "weather": [{"description": "clear sky"}],
                    "wind": {"speed": 3.5}
                }
            ]
        }
        
        report = format_weather_report(current_data, forecast_data, "New York")
        
        self.assertIn("New York, US", report)
        self.assertIn("Clear sky", report)
        self.assertIn("20°C", report)
        self.assertIn("65%", report)
        self.assertIn("OpenWeatherMap", report)

    @patch('plugins_func.functions.get_weather.fetch_weather_data')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_weather_success(self, mock_cache_manager, mock_fetch):
        """Test successful weather plugin execution."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock weather data
        current_data = {
            "name": "New York",
            "sys": {"country": "US"},
            "main": {"temp": 20, "feels_like": 18, "humidity": 65, "pressure": 1013, "temp_min": 15, "temp_max": 25},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 3.5, "deg": 180}
        }
        mock_fetch.return_value = (current_data, None)
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_weather(self.mock_conn, "New York", "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIsNotNone(result.result)
        
        # Verify cache was set
        mock_cache_manager.set.assert_called_once()

    @patch('core.utils.cache.manager.cache_manager')
    def test_get_weather_cache_hit(self, mock_cache_manager):
        """Test weather plugin with cache hit."""
        # Mock cache hit
        cached_report = "Cached weather report"
        mock_cache_manager.get.return_value = cached_report
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_weather(self.mock_conn, "New York", "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertEqual(result.result, cached_report)

    def test_get_weather_no_api_key(self):
        """Test weather plugin without API key."""
        self.mock_conn.config["plugins"]["get_weather"]["api_key"] = "your_openweathermap_api_key"
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_weather(self.mock_conn, "New York", "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("not configured", result.result)

    @patch('plugins_func.functions.get_weather.fetch_weather_data')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_weather_api_failure(self, mock_cache_manager, mock_fetch):
        """Test weather plugin with API failure."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock API failure
        mock_fetch.return_value = (None, None)
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_weather(self.mock_conn, "InvalidCity", "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("Unable to get weather data", result.result)

    @patch('plugins_func.functions.get_weather.get_ip_info')
    @patch('plugins_func.functions.get_weather.fetch_weather_data')
    @patch('core.utils.cache.manager.cache_manager')
    def test_get_weather_ip_location(self, mock_cache_manager, mock_fetch, mock_get_ip_info):
        """Test weather plugin with IP-based location detection."""
        # Mock cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock IP info
        mock_get_ip_info.return_value = {"city": "London"}
        mock_cache_manager.get.return_value = None  # IP cache miss
        
        # Mock weather data
        current_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 15, "feels_like": 13, "humidity": 70, "pressure": 1015, "temp_min": 10, "temp_max": 20},
            "weather": [{"description": "overcast clouds"}],
            "wind": {"speed": 2.5}
        }
        mock_fetch.return_value = (current_data, None)
        
        from plugins_func.register import ActionResponse, Action
        
        result = get_weather(self.mock_conn, None, "en_US")
        
        self.assertIsInstance(result, ActionResponse)
        self.assertEqual(result.action, Action.REQLLM)
        self.assertIn("London, GB", result.result)


if __name__ == '__main__':
    unittest.main()
