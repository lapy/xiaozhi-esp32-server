# Weather Plugin Integration

This document describes how to use and configure the Weather plugin using OpenWeatherMap API for getting weather information from a reliable weather service.

## Overview

The Weather plugin (`get_weather`) allows users to get current weather conditions and forecasts for any location worldwide using the OpenWeatherMap API. It provides comprehensive weather data including current conditions, detailed parameters, and 5-day forecasts.

## Features

- **Global Coverage**: Weather data for any location worldwide
- **Current Conditions**: Temperature, humidity, pressure, wind, visibility
- **5-Day Forecast**: Detailed daily forecasts with temperature ranges
- **Multiple Languages**: Support for various languages (English, Japanese, Spanish, French, German)
- **IP-Based Location**: Automatically detects user location from IP address
- **Caching**: 10-minute cache to reduce API calls and improve performance
- **Error Handling**: Robust error handling with user-friendly messages

## Configuration

### 1. Plugin Configuration (config.yaml)

```yaml
plugins:
  get_weather:
    api_key: "your_openweathermap_api_key"
    default_location: "New York"
```

### 2. Enable Plugin

Add the plugin to the functions list in `config.yaml`:

```yaml
Intent:
  intent_llm:
    functions:
      - get_weather
      - get_news
      - play_music
  function_call:
    functions:
      - change_role
      - get_weather
      - get_news
      - play_music
```

### 3. Database Configuration

The plugin is automatically registered in the database with the following configuration:

- **Plugin Name**: `get_weather`
- **Display Name**: `Weather Service`
- **API Key**: OpenWeatherMap API key (configurable)
- **Default Location**: New York (configurable)

## API Setup

### OpenWeatherMap API Key

1. **Sign Up**: Visit [OpenWeatherMap](https://openweathermap.org/api) and create a free account
2. **Get API Key**: Navigate to your account dashboard and copy your API key
3. **Configure**: Replace `your_openweathermap_api_key` in the configuration with your actual API key

### API Limits

- **Free Tier**: 1000 calls per day, 60 calls per minute
- **Paid Plans**: Available for higher usage requirements
- **Caching**: Plugin uses 10-minute caching to minimize API calls

## Usage Examples

### Basic Weather Query
```
User: "What's the weather like?"
→ Gets weather for user's detected location or default location

User: "What's the weather in London?"
→ Gets current weather and 5-day forecast for London

User: "How's the weather in Tokyo?"
→ Gets weather information for Tokyo
```

### Advanced Queries
```
User: "What's the weather in Los Angeles, CA?"
→ Gets weather for Los Angeles, California

User: "Weather forecast for Paris, France"
→ Gets 5-day forecast for Paris

User: "Tell me about the weather in Sydney"
→ Gets comprehensive weather information for Sydney
```

## Supported Locations

The plugin supports any location worldwide that OpenWeatherMap covers:

- **Cities**: New York, London, Tokyo, Paris, etc.
- **Cities with State/Province**: Los Angeles, CA; Toronto, ON; etc.
- **Cities with Country**: London, UK; Tokyo, Japan; etc.
- **International Locations**: Any city worldwide

## Weather Data Provided

### Current Conditions
- **Temperature**: Current temperature and "feels like" temperature
- **Conditions**: Weather description (sunny, cloudy, rain, etc.)
- **Temperature Range**: Daily minimum and maximum temperatures
- **Humidity**: Relative humidity percentage
- **Pressure**: Atmospheric pressure in hPa
- **Wind**: Wind speed and direction
- **Visibility**: Visibility distance in kilometers

### 5-Day Forecast
- **Daily Summary**: Most common weather condition for each day
- **Temperature Range**: Daily high and low temperatures
- **Average Humidity**: Daily average humidity
- **Average Wind Speed**: Daily average wind speed

## Language Support

The plugin supports multiple languages for weather descriptions:

| Language Code | Description |
|---------------|-------------|
| `en_US` | English (default) |
| `ja_JP` | Japanese |
| `es_ES` | Spanish |
| `fr_FR` | French |
| `de_DE` | German |

## Technical Details

### API Endpoints Used

1. **Current Weather**: `https://api.openweathermap.org/data/2.5/weather`
   - Provides current weather conditions
   - Parameters: location, API key, units (metric), language

2. **5-Day Forecast**: `https://api.openweathermap.org/data/2.5/forecast`
   - Provides 5-day weather forecast
   - Parameters: location, API key, units (metric), language

### Data Processing

- **Weather Conditions**: Standardized weather condition descriptions
- **Temperature**: Converted to Celsius (°C)
- **Wind Direction**: Converted to compass directions (N, NE, E, etc.)
- **Forecast Grouping**: Daily forecasts grouped from hourly data

### Caching Strategy

- **Cache Key**: `western_weather_{location}_{lang}`
- **Cache Duration**: 10 minutes (600 seconds)
- **Cache Type**: Weather cache type from cache manager

## Error Handling

The plugin handles various error scenarios:

1. **API Key Not Configured**: Returns helpful message to contact administrator
2. **Invalid Location**: Returns error message asking user to check location name
3. **API Errors**: Logs detailed error information and returns user-friendly message
4. **Network Issues**: Handles timeouts and connection errors gracefully

## Migration from Previous Weather Service

If migrating from a previous weather service:

1. **Replace Plugin**: Change weather plugin configuration
2. **Update API Key**: Replace previous API key with OpenWeatherMap API key
3. **Update Default Location**: Change default location to Western city
4. **Test Functionality**: Verify weather queries work correctly

## Performance Considerations

- **API Limits**: Monitor daily API usage to avoid hitting limits
- **Caching**: 10-minute cache significantly reduces API calls
- **Error Handling**: Graceful degradation when API is unavailable
- **Timeout**: 10-second timeout prevents long waits

## Security Notes

- **API Key Protection**: Store API key securely and don't commit to version control
- **Input Validation**: Location input is validated by the API
- **Rate Limiting**: Built-in caching helps prevent rate limit issues

## Troubleshooting

### Common Issues

1. **"Weather service not configured"**
   - Solution: Configure OpenWeatherMap API key in settings

2. **"Unable to get weather data"**
   - Solution: Check if location name is correct and spelled properly

3. **API rate limit exceeded**
   - Solution: Wait for rate limit reset or upgrade to paid plan

### Debug Information

Check logs for detailed error information:
- API response codes and error messages
- Location parsing issues
- Network connectivity problems

## Conclusion

The Western Weather plugin provides reliable, comprehensive weather information using the industry-standard OpenWeatherMap API. With global coverage, multiple language support, and robust error handling, it's suitable for production use in Western markets.
