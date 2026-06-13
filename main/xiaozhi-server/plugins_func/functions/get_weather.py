import requests
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action
import core.utils.cache.manager as cache_module
from core.utils.util import get_ip_info
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

GET_WEATHER_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get the weather for a location. If the user does not specify a location, "
            "try resolving it from IP address and fall back to the configured default."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name such as New York, optional.",
                },
                "lang": {
                    "type": "string",
                    "description": "Language code for the response, defaults to en_US.",
                },
            },
            "required": ["lang"],
        },
    },
}

WEATHER_CONDITION_MAP = {
    "clear sky": "Clear sky",
    "broken clouds": "Broken clouds",
    "few clouds": "Few clouds",
    "scattered clouds": "Scattered clouds",
    "light rain": "Light rain",
    "moderate rain": "Moderate rain",
    "heavy rain": "Heavy rain",
    "light snow": "Light snow",
    "snow": "Snow",
}


def get_weather_condition(description: Optional[str]) -> str:
    if not description:
        return "Unknown Condition"
    normalized = description.strip().lower()
    return WEATHER_CONDITION_MAP.get(
        normalized,
        description.strip().title(),
    )


def fetch_weather_data(location: str, api_key: str) -> Tuple[Optional[dict], Optional[dict]]:
    try:
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
            "lang": "en",
        }

        current_response = requests.get(current_url, params=params, timeout=10)
        if current_response.status_code != 200:
            return None, None

        forecast_response = requests.get(forecast_url, params=params, timeout=10)
        if forecast_response.status_code != 200:
            return current_response.json(), None

        return current_response.json(), forecast_response.json()
    except Exception as e:
        logger.bind(tag=TAG).error(f"Failed to fetch weather data: {e}")
        return None, None


def format_weather_report(current_data: dict, forecast_data: Optional[dict], location: str) -> str:
    country = current_data.get("sys", {}).get("country", "")
    weather_desc = current_data.get("weather", [{}])[0].get("description", "")
    condition = get_weather_condition(weather_desc)
    main = current_data.get("main", {})
    wind = current_data.get("wind", {})

    report = [
        f"{location}, {country}".strip(", "),
        f"Current weather: {condition}",
        f"Temperature: {main.get('temp', 'N/A')}°C",
        f"Feels like: {main.get('feels_like', 'N/A')}°C",
        f"Humidity: {main.get('humidity', 'N/A')}%",
        f"Pressure: {main.get('pressure', 'N/A')} hPa",
        f"Wind speed: {wind.get('speed', 'N/A')} m/s",
        "Source: OpenWeatherMap",
    ]

    if forecast_data and forecast_data.get("list"):
        report.append("Forecast:")
        for item in forecast_data["list"][:3]:
            desc = item.get("weather", [{}])[0].get("description", "")
            forecast_condition = get_weather_condition(desc)
            temp = item.get("main", {}).get("temp", "N/A")
            report.append(f"- {item.get('dt_txt', 'Unknown time')}: {forecast_condition}, {temp}°C")

    return "\n".join(report)


@register_function("get_weather", GET_WEATHER_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_weather(conn: "ConnectionHandler", location: str = None, lang: str = "en_US"):
    weather_config = conn.config.get("plugins", {}).get("get_weather", {})
    api_key = weather_config.get("api_key", "")
    default_location = weather_config.get("default_location", "New York")
    if not api_key or api_key == "your_openweathermap_api_key":
        return ActionResponse(Action.REQLLM, "Weather API key is not configured", None)

    if not location:
        client_ip = getattr(conn, "client_ip", None)
        if client_ip:
            cached_ip_info = cache_module.cache_manager.get(cache_module.CacheType.IP_INFO, client_ip)
            if cached_ip_info:
                location = cached_ip_info.get("city")
            else:
                ip_info = get_ip_info(client_ip, logger)
                if ip_info:
                    cache_module.cache_manager.set(cache_module.CacheType.IP_INFO, client_ip, ip_info)
                    location = ip_info.get("city")
        if not location:
            location = default_location

    weather_cache_key = f"weather_{location}_{lang}"
    cached_weather_report = cache_module.cache_manager.get(cache_module.CacheType.WEATHER, weather_cache_key)
    if cached_weather_report:
        return ActionResponse(Action.REQLLM, cached_weather_report, None)

    current_data, forecast_data = fetch_weather_data(location, api_key)
    if not current_data:
        return ActionResponse(Action.REQLLM, f"Unable to get weather data for {location}", None)

    report = format_weather_report(current_data, forecast_data, location)
    cache_module.cache_manager.set(cache_module.CacheType.WEATHER, weather_cache_key, report)
    return ActionResponse(Action.REQLLM, report, None)
