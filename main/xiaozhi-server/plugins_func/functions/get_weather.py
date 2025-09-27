import requests
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action
from core.utils.util import get_ip_info

TAG = __name__
logger = setup_logging()

GET_WEATHER_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Get weather information for any location worldwide using OpenWeatherMap API. "
            "Users can specify a city name, state/province, or country. Examples: 'New York weather', 'London weather', 'Tokyo weather'. "
            "If no location is specified, uses the user's detected location or default location. "
            "Provides current conditions, detailed weather parameters, and 5-day forecast."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name (city, state, country), e.g., 'New York', 'London', 'Tokyo', 'Los Angeles, CA'. Optional parameter, if not provided uses detected or default location",
                },
                "lang": {
                    "type": "string",
                    "description": "Language code for user response, e.g., en_US/zh_CN/zh_HK/ja_JP, defaults to en_US",
                },
            },
            "required": ["lang"],
        },
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Weather condition mapping from OpenWeatherMap
WEATHER_CONDITIONS = {
    # Clear sky
    "clear sky": "Clear sky",
    "sunny": "Sunny",
    
    # Clouds
    "few clouds": "Few clouds",
    "scattered clouds": "Scattered clouds", 
    "broken clouds": "Broken clouds",
    "overcast clouds": "Overcast clouds",
    "partly cloudy": "Partly cloudy",
    "mostly cloudy": "Mostly cloudy",
    "cloudy": "Cloudy",
    
    # Rain
    "light rain": "Light rain",
    "moderate rain": "Moderate rain",
    "heavy rain": "Heavy rain",
    "very heavy rain": "Very heavy rain",
    "extreme rain": "Extreme rain",
    "freezing rain": "Freezing rain",
    "light intensity shower rain": "Light shower",
    "shower rain": "Shower",
    "heavy intensity shower rain": "Heavy shower",
    "ragged shower rain": "Ragged shower",
    
    # Thunderstorm
    "thunderstorm with light rain": "Light thunderstorm",
    "thunderstorm with rain": "Thunderstorm with rain",
    "thunderstorm with heavy rain": "Heavy thunderstorm",
    "light thunderstorm": "Light thunderstorm",
    "thunderstorm": "Thunderstorm",
    "heavy thunderstorm": "Heavy thunderstorm",
    "ragged thunderstorm": "Ragged thunderstorm",
    "thunderstorm with light drizzle": "Light thunderstorm with drizzle",
    "thunderstorm with drizzle": "Thunderstorm with drizzle",
    "thunderstorm with heavy drizzle": "Heavy thunderstorm with drizzle",
    
    # Drizzle
    "light intensity drizzle": "Light drizzle",
    "drizzle": "Drizzle",
    "heavy intensity drizzle": "Heavy drizzle",
    "light intensity drizzle rain": "Light drizzle rain",
    "drizzle rain": "Drizzle rain",
    "heavy intensity drizzle rain": "Heavy drizzle rain",
    "shower rain and drizzle": "Shower rain and drizzle",
    "heavy shower rain and drizzle": "Heavy shower rain and drizzle",
    "shower drizzle": "Shower drizzle",
    
    # Snow
    "light snow": "Light snow",
    "snow": "Snow",
    "heavy snow": "Heavy snow",
    "sleet": "Sleet",
    "light shower sleet": "Light shower sleet",
    "shower sleet": "Shower sleet",
    "light rain and snow": "Light rain and snow",
    "rain and snow": "Rain and snow",
    "light shower snow": "Light shower snow",
    "shower snow": "Shower snow",
    "heavy shower snow": "Heavy shower snow",
    
    # Mist/Fog
    "mist": "Mist",
    "smoke": "Smoke",
    "haze": "Haze",
    "sand/dust whirls": "Sand/dust whirls",
    "fog": "Fog",
    "sand": "Sand",
    "dust": "Dust",
    "volcanic ash": "Volcanic ash",
    "squalls": "Squalls",
    "tornado": "Tornado",
    "tropical storm": "Tropical storm",
    "hurricane": "Hurricane",
    "cold": "Cold",
    "hot": "Hot",
    "windy": "Windy",
    "hail": "Hail",
    "calm": "Calm",
    "light breeze": "Light breeze",
    "gentle breeze": "Gentle breeze",
    "moderate breeze": "Moderate breeze",
    "fresh breeze": "Fresh breeze",
    "strong breeze": "Strong breeze",
    "high wind, near gale": "High wind, near gale",
    "gale": "Gale",
    "severe gale": "Severe gale",
    "storm": "Storm",
    "violent storm": "Violent storm",
    "hurricane-force wind": "Hurricane-force wind",
    "clear": "Clear"
}


def get_weather_condition(description):
    """Get standardized weather condition from OpenWeatherMap description"""
    description_lower = description.lower()
    return WEATHER_CONDITIONS.get(description_lower, description.title())


def fetch_weather_data(location, api_key, lang="en"):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        # Current weather endpoint
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric&lang={lang}"
        
        # 5-day forecast endpoint
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&units=metric&lang={lang}"
        
        current_response = requests.get(current_url, headers=HEADERS, timeout=10)
        forecast_response = requests.get(forecast_url, headers=HEADERS, timeout=10)
        
        if current_response.status_code != 200:
            logger.bind(tag=TAG).error(f"Current weather API error: {current_response.status_code} - {current_response.text}")
            return None, None
            
        if forecast_response.status_code != 200:
            logger.bind(tag=TAG).error(f"Forecast API error: {forecast_response.status_code} - {forecast_response.text}")
            return current_response.json(), None
            
        return current_response.json(), forecast_response.json()
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"Error fetching weather data: {e}")
        return None, None


def format_weather_report(current_data, forecast_data, location, lang="en_US"):
    """Format weather data into a readable report"""
    if not current_data:
        return f"Unable to get weather data for {location}. Please check the location name and try again."
    
    # Basic location info
    city_name = current_data.get("name", location)
    country = current_data.get("sys", {}).get("country", "")
    full_location = f"{city_name}, {country}" if country else city_name
    
    # Current weather
    main = current_data.get("main", {})
    weather = current_data.get("weather", [{}])[0]
    wind = current_data.get("wind", {})
    
    temp = round(main.get("temp", 0))
    feels_like = round(main.get("feels_like", 0))
    humidity = main.get("humidity", 0)
    pressure = main.get("pressure", 0)
    temp_min = round(main.get("temp_min", 0))
    temp_max = round(main.get("temp_max", 0))
    
    condition = get_weather_condition(weather.get("description", "Unknown"))
    wind_speed = wind.get("speed", 0)
    wind_deg = wind.get("deg", 0)
    visibility = current_data.get("visibility", 0) / 1000 if current_data.get("visibility") else None
    
    # Build weather report
    report = f"Weather for {full_location}:\n\n"
    report += f"Current Conditions: {condition}\n"
    report += f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
    report += f"Temperature Range: {temp_min}°C to {temp_max}°C\n"
    report += f"Humidity: {humidity}%\n"
    report += f"Pressure: {pressure} hPa\n"
    
    if wind_speed > 0:
        report += f"Wind: {wind_speed} m/s"
        if wind_deg:
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            direction = directions[int((wind_deg + 11.25) / 22.5) % 16]
            report += f" from {direction}"
        report += "\n"
    
    if visibility:
        report += f"Visibility: {visibility:.1f} km\n"
    
    # 5-day forecast (group by day)
    if forecast_data and "list" in forecast_data:
        report += "\n5-Day Forecast:\n"
        
        daily_forecasts = {}
        for item in forecast_data["list"]:
            date = item["dt_txt"].split(" ")[0]  # Get date part
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "temps": [],
                    "conditions": [],
                    "humidity": [],
                    "wind": []
                }
            
            daily_forecasts[date]["temps"].append(round(item["main"]["temp"]))
            daily_forecasts[date]["conditions"].append(get_weather_condition(item["weather"][0]["description"]))
            daily_forecasts[date]["humidity"].append(item["main"]["humidity"])
            daily_forecasts[date]["wind"].append(item["wind"]["speed"])
        
        # Format daily forecasts
        import datetime
        for i, (date, data) in enumerate(list(daily_forecasts.items())[:5]):
            try:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                date_str = date_obj.strftime("%m/%d")
            except:
                day_name = f"Day {i+1}"
                date_str = date
            
            min_temp = min(data["temps"])
            max_temp = max(data["temps"])
            avg_humidity = round(sum(data["humidity"]) / len(data["humidity"]))
            avg_wind = round(sum(data["wind"]) / len(data["wind"]), 1)
            
            # Most common condition for the day
            condition_count = {}
            for condition in data["conditions"]:
                condition_count[condition] = condition_count.get(condition, 0) + 1
            most_common_condition = max(condition_count, key=condition_count.get)
            
            report += f"{day_name} ({date_str}): {most_common_condition}, {min_temp}°C to {max_temp}°C, {avg_humidity}% humidity, {avg_wind} m/s wind\n"
    
    report += "\n(Data provided by OpenWeatherMap)"
    
    return report


@register_function("get_weather", GET_WEATHER_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_weather(conn, location: str = None, lang: str = "en_US"):
    from core.utils.cache.manager import cache_manager, CacheType

    api_key = conn.config["plugins"]["get_weather"].get(
        "api_key", "your_openweathermap_api_key"
    )
    default_location = conn.config["plugins"]["get_weather"].get(
        "default_location", "New York"
    )
    client_ip = conn.client_ip

    # Check if API key is configured
    if api_key == "your_openweathermap_api_key":
        return ActionResponse(
            Action.REQLLM, 
            "Weather service not configured. Please contact administrator to set up OpenWeatherMap API key.", 
            None
        )

    # Determine location
    if not location:
        # Try to get location from client IP
        if client_ip:
            cached_ip_info = cache_manager.get(CacheType.IP_INFO, client_ip)
            if cached_ip_info:
                location = cached_ip_info.get("city")
            else:
                ip_info = get_ip_info(client_ip, logger)
                if ip_info:
                    cache_manager.set(CacheType.IP_INFO, client_ip, ip_info)
                    location = ip_info.get("city")
        
        # Fall back to default location
        if not location:
            location = default_location

    # Check cache first
    weather_cache_key = f"weather_{location}_{lang}"
    cached_weather_report = cache_manager.get(CacheType.WEATHER, weather_cache_key)
    if cached_weather_report:
        return ActionResponse(Action.REQLLM, cached_weather_report, None)

    # Convert language code for API
    api_lang = "en"
    if lang.startswith("zh"):
        api_lang = "zh_cn"
    elif lang.startswith("ja"):
        api_lang = "ja"
    elif lang.startswith("es"):
        api_lang = "es"
    elif lang.startswith("fr"):
        api_lang = "fr"
    elif lang.startswith("de"):
        api_lang = "de"

    # Fetch weather data
    current_data, forecast_data = fetch_weather_data(location, api_key, api_lang)
    
    if not current_data:
        error_msg = f"Unable to get weather data for '{location}'. Please check if the location name is correct and try again."
        return ActionResponse(Action.REQLLM, error_msg, None)

    # Format weather report
    weather_report = format_weather_report(current_data, forecast_data, location, lang)
    
    # Cache the weather report for 10 minutes
    cache_manager.set(CacheType.WEATHER, weather_cache_key, weather_report, ttl=600)
    
    return ActionResponse(Action.REQLLM, weather_report, None)
