# Weather Plugin Usage Guide

## Overview

The weather plugin `get_weather` is one of the core features of Xiaozhi ESP32 voice assistant, supporting voice queries for weather information worldwide. The plugin is based on QWeather API, providing real-time weather and 7-day weather forecast functionality.

## API Key Application Guide

### 1. Register QWeather Account

1. Visit [QWeather Console](https://console.qweather.com/)
2. Register account and complete email verification
3. Login to console

### 2. Create Application to Get API Key

1. After entering the console, click ["Project Management"](https://console.qweather.com/project?lang=zh) → "Create Project"
2. Fill in project information:
   - **Project Name**: e.g., "Xiaozhi Voice Assistant"
3. Click Save
4. After project creation is complete, click "Create Credentials" in the project
5. Fill in credential information:
    - **Credential Name**: e.g., "Xiaozhi Voice Assistant"
    - **Authentication Method**: Select "API Key"
6. Click Save
7. Copy the `API Key` from the credentials, this is the first key configuration information

### 3. Get API Host

1. In the console, click ["Settings"](https://console.qweather.com/setting?lang=zh) → "API Host"
2. View the exclusive `API Host` address assigned to you, this is the second key configuration information

The above operations will give you two important configuration information: `API Key` and `API Host`

## Configuration Methods (Choose One)

### Method 1. If you use Smart Control Panel deployment (Recommended)

1. Login to Smart Control Panel
2. Enter "Role Configuration" page
3. Select the agent to configure
4. Click "Edit Functions" button
5. Find "Weather Query" plugin in the right parameter configuration area
6. Check "Weather Query"
7. Fill the first key configuration `API Key` into `Weather Plugin API Key`
8. Fill the second key configuration `API Host` into `Developer API Host`
9. Save configuration, then save agent configuration

### Method 2. If you only deploy single module xiaozhi-server

Configure in `data/.config.yaml`:

1. Fill the first key configuration `API Key` into `api_key`
2. Fill the second key configuration `API Host` into `api_host`
3. Fill your city into `default_location`, e.g., `Guangzhou`

```yaml
plugins:
  get_weather:
    api_key: "Your QWeather API key"
    api_host: "Your QWeather API host address"
    default_location: "Your default query city"
```

