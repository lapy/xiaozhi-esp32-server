import requests
from bs4 import BeautifulSoup
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
            "Get weather for a specific location, user should provide a location, for example if user says 'Hangzhou weather', parameter is: Hangzhou."
            "If user mentions a province, default to the provincial capital city. If user mentions a place name that is not a province or city, default to the provincial capital of that place."
            "If user doesn't specify a location, says 'how's the weather', 'what's today's weather like', location parameter is empty"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name, for example Hangzhou. Optional parameter, if not provided then not passed",
                },
                "lang": {
                    "type": "string",
                    "description": "Language code for user response, such as zh_CN/zh_HK/en_US/ja_JP, etc., defaults to zh_CN",
                },
            },
            "required": ["lang"],
        },
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    )
}

# Weather codes https://dev.qweather.com/docs/resource/icons/#weather-icons
WEATHER_CODE_MAP = {
    "100": "Clear",
    "101": "Cloudy",
    "102": "Partly Cloudy",
    "103": "Clear to Cloudy",
    "104": "Overcast",
    "150": "Clear",
    "151": "Cloudy",
    "152": "Partly Cloudy",
    "153": "Clear to Cloudy",
    "300": "Shower",
    "301": "Heavy Shower",
    "302": "Thunderstorm",
    "303": "Heavy Thunderstorm",
    "304": "Thunderstorm with Hail",
    "305": "Light Rain",
    "306": "Moderate Rain",
    "307": "Heavy Rain",
    "308": "Extreme Rain",
    "309": "Drizzle",
    "310": "Rainstorm",
    "311": "Heavy Rainstorm",
    "312": "Severe Rainstorm",
    "313": "Freezing Rain",
    "314": "Light to Moderate Rain",
    "315": "Moderate to Heavy Rain",
    "316": "Heavy Rain to Rainstorm",
    "317": "Rainstorm to Heavy Rainstorm",
    "318": "Heavy Rainstorm to Severe Rainstorm",
    "350": "Shower",
    "351": "Heavy Shower",
    "399": "Rain",
    "400": "Light Snow",
    "401": "Moderate Snow",
    "402": "Heavy Snow",
    "403": "Snowstorm",
    "404": "Sleet",
    "405": "Rain and Snow",
    "406": "Shower with Snow",
    "407": "Snow Shower",
    "408": "Light to Moderate Snow",
    "409": "Moderate to Heavy Snow",
    "410": "Heavy Snow to Snowstorm",
    "456": "Shower with Snow",
    "457": "Snow Shower",
    "499": "Snow",
    "500": "Thin Fog",
    "501": "Fog",
    "502": "Haze",
    "503": "Blowing Sand",
    "504": "Floating Dust",
    "507": "Sandstorm",
    "508": "Heavy Sandstorm",
    "509": "Dense Fog",
    "510": "Heavy Dense Fog",
    "511": "Moderate Haze",
    "512": "Heavy Haze",
    "513": "Severe Haze",
    "514": "Heavy Fog",
    "515": "Extremely Heavy Fog",
    "900": "Hot",
    "901": "Cold",
    "999": "Unknown",
}


def fetch_city_info(location, api_key, api_host):
    url = f"https://{api_host}/geo/v2/city/lookup?key={api_key}&location={location}&lang=zh"
    response = requests.get(url, headers=HEADERS).json()
    if response.get("error") is not None:
        logger.bind(tag=TAG).error(
            f"Failed to get weather, reason: {response.get('error', {}).get('detail')}"
        )
        return None
    return response.get("location", [])[0] if response.get("location") else None


def fetch_weather_page(url):
    response = requests.get(url, headers=HEADERS)
    return BeautifulSoup(response.text, "html.parser") if response.ok else None


def parse_weather_info(soup):
    city_name = soup.select_one("h1.c-submenu__location").get_text(strip=True)

    current_abstract = soup.select_one(".c-city-weather-current .current-abstract")
    current_abstract = (
        current_abstract.get_text(strip=True) if current_abstract else "Unknown"
    )

    current_basic = {}
    for item in soup.select(
        ".c-city-weather-current .current-basic .current-basic___item"
    ):
        parts = item.get_text(strip=True, separator=" ").split(" ")
        if len(parts) == 2:
            key, value = parts[1], parts[0]
            current_basic[key] = value

    temps_list = []
    for row in soup.select(".city-forecast-tabs__row")[:7]:  # Get first 7 days of data
        date = row.select_one(".date-bg .date").get_text(strip=True)
        weather_code = (
            row.select_one(".date-bg .icon")["src"].split("/")[-1].split(".")[0]
        )
        weather = WEATHER_CODE_MAP.get(weather_code, "Unknown")
        temps = [span.get_text(strip=True) for span in row.select(".tmp-cont .temp")]
        high_temp, low_temp = (temps[0], temps[-1]) if len(temps) >= 2 else (None, None)
        temps_list.append((date, weather, high_temp, low_temp))

    return city_name, current_abstract, current_basic, temps_list


@register_function("get_weather", GET_WEATHER_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_weather(conn, location: str = None, lang: str = "zh_CN"):
    from core.utils.cache.manager import cache_manager, CacheType

    api_host = conn.config["plugins"]["get_weather"].get(
        "api_host", "mj7p3y7naa.re.qweatherapi.com"
    )
    api_key = conn.config["plugins"]["get_weather"].get(
        "api_key", "a861d0d5e7bf4ee1a83d9a9e4f96d4da"
    )
    default_location = conn.config["plugins"]["get_weather"]["default_location"]
    client_ip = conn.client_ip

    # Prioritize using user-provided location parameter
    if not location:
        # Parse city through client IP
        if client_ip:
            # First try to get city information from cache for IP
            cached_ip_info = cache_manager.get(CacheType.IP_INFO, client_ip)
            if cached_ip_info:
                location = cached_ip_info.get("city")
            else:
                # Cache miss, call API to get
                ip_info = get_ip_info(client_ip, logger)
                if ip_info:
                    cache_manager.set(CacheType.IP_INFO, client_ip, ip_info)
                    location = ip_info.get("city")

            if not location:
                location = default_location
        else:
            # If no IP, use default location
            location = default_location
    # Try to get complete weather report from cache
    weather_cache_key = f"full_weather_{location}_{lang}"
    cached_weather_report = cache_manager.get(CacheType.WEATHER, weather_cache_key)
    if cached_weather_report:
        return ActionResponse(Action.REQLLM, cached_weather_report, None)

    # Cache miss, get real-time weather data
    city_info = fetch_city_info(location, api_key, api_host)
    if not city_info:
        return ActionResponse(
            Action.REQLLM, f"City not found: {location}, please confirm if the location is correct", None
        )
    soup = fetch_weather_page(city_info["fxLink"])
    if not soup:
        return ActionResponse(Action.REQLLM, None, "Request failed")
    city_name, current_abstract, current_basic, temps_list = parse_weather_info(soup)

    weather_report = f"Your queried location is: {city_name}\n\nCurrent weather: {current_abstract}\n"

    # Add valid current weather parameters
    if current_basic:
        weather_report += "Detailed parameters:\n"
        for key, value in current_basic.items():
            if value != "0":  # Filter invalid values
                weather_report += f"  · {key}: {value}\n"

    # Add 7-day forecast
    weather_report += "\n7-day forecast:\n"
    for date, weather, high, low in temps_list:
        weather_report += f"{date}: {weather}, temperature {low}~{high}\n"

    # Prompt
    weather_report += "\n(If you need specific weather for a particular day, please tell me the date)"

    # Cache complete weather report
    cache_manager.set(CacheType.WEATHER, weather_cache_key, weather_report)

    return ActionResponse(Action.REQLLM, weather_report, None)
