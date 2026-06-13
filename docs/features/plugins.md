# 🔌 Plugin System

This guide covers the Xiaozhi ESP32 Server plugin system, including how to create, configure, and manage plugins for extending functionality.

## 🎯 Plugin System Overview

The plugin system allows you to:
- **Extend functionality** with custom features
- **Integrate third-party services** and APIs
- **Create reusable components** for different use cases
- **Modularize complex functionality** into manageable pieces

## 🔧 Plugin Architecture

### **Plugin Structure**

```
plugins/
├── __init__.py
├── base/
│   ├── __init__.py
│   └── plugin.py
├── weather/
│   ├── __init__.py
│   ├── weather_plugin.py
│   └── config.yaml
├── news/
│   ├── __init__.py
│   ├── news_plugin.py
│   └── config.yaml
└── custom/
    ├── __init__.py
    ├── my_plugin.py
    └── config.yaml
```

### **Base Plugin Class**

```python
# plugins/base/plugin.py
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """Base class for all Xiaozhi plugins"""
    
    def __init__(self, config):
        self.config = config
        self.name = config.get('name', 'Unknown Plugin')
        self.version = config.get('version', '1.0.0')
        self.enabled = config.get('enabled', False)
        self.logger = logging.getLogger(f"plugin.{self.name}")
    
    @abstractmethod
    def initialize(self):
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def process_command(self, command, context=None):
        """Process voice commands"""
        pass
    
    @abstractmethod
    def get_status(self):
        """Get plugin status"""
        pass
    
    def cleanup(self):
        """Cleanup plugin resources"""
        pass
    
    def validate_config(self, config):
        """Validate plugin configuration"""
        return True
```

## 🚀 Creating Your First Plugin

### **Step 1: Create Plugin Directory**

```bash
# Create plugin directory
mkdir -p plugins/my_first_plugin
cd plugins/my_first_plugin
```

### **Step 2: Create Plugin Files**

#### **Plugin Implementation**
```python
# plugins/my_first_plugin/my_first_plugin.py
from plugins.base.plugin import BasePlugin
import requests
import json

class MyFirstPlugin(BasePlugin):
    """My first custom plugin"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.endpoint = config.get('endpoint', 'https://api.example.com')
    
    def initialize(self):
        """Initialize the plugin"""
        self.logger.info(f"Initializing {self.name} v{self.version}")
        
        # Validate configuration
        if not self.api_key:
            raise ValueError("API key is required")
        
        # Test API connectivity
        try:
            response = requests.get(f"{self.endpoint}/health", timeout=10)
            response.raise_for_status()
            self.logger.info("Plugin initialized successfully")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to initialize plugin: {e}")
            raise
    
    def process_command(self, command, context=None):
        """Process voice commands"""
        self.logger.info(f"Processing command: {command}")
        
        # Parse command
        if "hello" in command.lower():
            return self._handle_hello()
        elif "status" in command.lower():
            return self._handle_status()
        else:
            return "I don't understand that command"
    
    def _handle_hello(self):
        """Handle hello command"""
        return "Hello! This is my first plugin speaking."
    
    def _handle_status(self):
        """Handle status command"""
        try:
            response = requests.get(f"{self.endpoint}/status", timeout=10)
            response.raise_for_status()
            data = response.json()
            return f"Plugin status: {data.get('status', 'unknown')}"
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get status: {e}")
            return "Sorry, I couldn't get the status"
    
    def get_status(self):
        """Get plugin status"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "status": "running" if self.enabled else "disabled"
        }
    
    def cleanup(self):
        """Cleanup plugin resources"""
        self.logger.info(f"Cleaning up {self.name}")
```

#### **Plugin Configuration**
```yaml
# plugins/my_first_plugin/config.yaml
name: "My First Plugin"
version: "1.0.0"
enabled: true
description: "A simple example plugin"

# Plugin-specific settings
api_key: "your-api-key-here"
endpoint: "https://api.example.com"
timeout: 30
retry_count: 3

# Command patterns
commands:
  - pattern: "hello"
    description: "Say hello"
  - pattern: "status"
    description: "Get plugin status"
```

#### **Plugin Initialization**
```python
# plugins/my_first_plugin/__init__.py
from .my_first_plugin import MyFirstPlugin

__all__ = ['MyFirstPlugin']
```

### **Step 3: Register Plugin**

```python
# plugins/__init__.py
from .my_first_plugin import MyFirstPlugin

PLUGINS = {
    'my_first_plugin': MyFirstPlugin,
}

def get_plugin(name):
    """Get plugin class by name"""
    return PLUGINS.get(name)

def list_plugins():
    """List all available plugins"""
    return list(PLUGINS.keys())
```

## 🔌 Plugin Configuration

### **Main Configuration**

```yaml
# In main config.yaml
plugins:
  enabled: true
  plugin_dir: plugins/
  auto_load: true
  
  # Plugin-specific configurations
  my_first_plugin:
    enabled: true
    api_key: "your-api-key-here"
    endpoint: "https://api.example.com"
    timeout: 30
  
  weather_plugin:
    enabled: true
    api_key: "your-weather-api-key"
    default_location: "New York, NY"
    units: "metric"
  
  news_plugin:
    enabled: true
    api_key: "your-news-api-key"
    sources: ["bbc-news", "cnn", "reuters"]
    max_articles: 10
```

### **Plugin-Specific Configuration**

```yaml
# plugins/weather_plugin/config.yaml
name: "Weather Plugin"
version: "1.0.0"
enabled: true
description: "Get weather information"

# Weather API settings
api_key: "your-openweathermap-api-key"
default_location: "New York, NY"
units: "metric"
cache_duration: 300

# Supported commands
commands:
  - pattern: "weather"
    description: "Get current weather"
  - pattern: "forecast"
    description: "Get weather forecast"
  - pattern: "temperature"
    description: "Get current temperature"
```

## 🌟 Advanced Plugin Features

### **Plugin Dependencies**

```python
# plugins/advanced_plugin/advanced_plugin.py
from plugins.base.plugin import BasePlugin
from plugins.weather_plugin import WeatherPlugin
from plugins.news_plugin import NewsPlugin

class AdvancedPlugin(BasePlugin):
    """Advanced plugin with dependencies"""
    
    def __init__(self, config):
        super().__init__(config)
        self.dependencies = config.get('dependencies', [])
        self.weather_plugin = None
        self.news_plugin = None
    
    def initialize(self):
        """Initialize plugin and dependencies"""
        self.logger.info(f"Initializing {self.name} with dependencies: {self.dependencies}")
        
        # Initialize dependencies
        for dep_name in self.dependencies:
            if dep_name == 'weather':
                self.weather_plugin = WeatherPlugin(self.config.get('weather', {}))
                self.weather_plugin.initialize()
            elif dep_name == 'news':
                self.news_plugin = NewsPlugin(self.config.get('news', {}))
                self.news_plugin.initialize()
    
    def process_command(self, command, context=None):
        """Process commands using dependencies"""
        if "weather" in command.lower() and self.weather_plugin:
            return self.weather_plugin.process_command(command, context)
        elif "news" in command.lower() and self.news_plugin:
            return self.news_plugin.process_command(command, context)
        else:
            return "I can help with weather and news. What would you like to know?"
```

### **Plugin Events and Hooks**

```python
# plugins/event_plugin/event_plugin.py
from plugins.base.plugin import BasePlugin
import asyncio

class EventPlugin(BasePlugin):
    """Plugin with event handling"""
    
    def __init__(self, config):
        super().__init__(config)
        self.events = {}
        self.hooks = {}
    
    def initialize(self):
        """Initialize plugin with event system"""
        self.logger.info(f"Initializing {self.name} with event system")
        
        # Register event handlers
        self.register_event('voice_command', self._handle_voice_command)
        self.register_event('system_startup', self._handle_system_startup)
        self.register_event('system_shutdown', self._handle_system_shutdown)
    
    def register_event(self, event_name, handler):
        """Register event handler"""
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(handler)
        self.logger.info(f"Registered handler for event: {event_name}")
    
    def emit_event(self, event_name, data=None):
        """Emit event to all handlers"""
        if event_name in self.events:
            for handler in self.events[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_name}: {e}")
    
    def _handle_voice_command(self, data):
        """Handle voice command events"""
        self.logger.info(f"Voice command received: {data}")
    
    def _handle_system_startup(self, data):
        """Handle system startup events"""
        self.logger.info("System startup detected")
    
    def _handle_system_shutdown(self, data):
        """Handle system shutdown events"""
        self.logger.info("System shutdown detected")
```

### **Plugin Caching**

```python
# plugins/cache_plugin/cache_plugin.py
from plugins.base.plugin import BasePlugin
import json
import time
from functools import wraps

class CachePlugin(BasePlugin):
    """Plugin with caching capabilities"""
    
    def __init__(self, config):
        super().__init__(config)
        self.cache = {}
        self.cache_duration = config.get('cache_duration', 300)  # 5 minutes
    
    def cache_result(self, duration=None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                current_time = time.time()
                
                # Check if cached result exists and is still valid
                if cache_key in self.cache:
                    cached_time, cached_result = self.cache[cache_key]
                    if current_time - cached_time < (duration or self.cache_duration):
                        self.logger.debug(f"Cache hit for {cache_key}")
                        return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.cache[cache_key] = (current_time, result)
                self.logger.debug(f"Cached result for {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def clear_cache(self, pattern=None):
        """Clear cache entries"""
        if pattern:
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
            self.logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")
        else:
            self.cache.clear()
            self.logger.info("Cleared all cache entries")
    
    @cache_result(duration=600)  # 10 minutes
    def expensive_operation(self, data):
        """Example of expensive operation with caching"""
        self.logger.info("Performing expensive operation...")
        time.sleep(2)  # Simulate expensive operation
        return f"Processed: {data}"
```

## 🔧 Plugin Management

### **Plugin Loader**

```python
# plugins/plugin_loader.py
import os
import yaml
import importlib
import logging

logger = logging.getLogger(__name__)

class PluginLoader:
    """Plugin loader and manager"""
    
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.loaded_plugins = {}
        self.plugin_configs = {}
    
    def load_plugins(self, config):
        """Load all enabled plugins"""
        logger.info("Loading plugins...")
        
        # Scan plugin directory
        for plugin_name in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            if os.path.isdir(plugin_path) and not plugin_name.startswith('_'):
                self._load_plugin(plugin_name, plugin_path, config)
        
        logger.info(f"Loaded {len(self.loaded_plugins)} plugins")
    
    def _load_plugin(self, plugin_name, plugin_path, config):
        """Load individual plugin"""
        try:
            # Load plugin configuration
            config_file = os.path.join(plugin_path, "config.yaml")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    plugin_config = yaml.safe_load(f)
            else:
                plugin_config = {}
            
            # Merge with main config
            plugin_config.update(config.get('plugins', {}).get(plugin_name, {}))
            
            # Check if plugin is enabled
            if not plugin_config.get('enabled', False):
                logger.info(f"Plugin {plugin_name} is disabled, skipping")
                return
            
            # Import plugin module
            module_name = f"plugins.{plugin_name}"
            module = importlib.import_module(module_name)
            
            # Get plugin class
            plugin_class = getattr(module, plugin_name.title().replace('_', ''))
            
            # Initialize plugin
            plugin_instance = plugin_class(plugin_config)
            plugin_instance.initialize()
            
            # Store plugin
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_configs[plugin_name] = plugin_config
            
            logger.info(f"Successfully loaded plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
    def get_plugin(self, name):
        """Get plugin instance by name"""
        return self.loaded_plugins.get(name)
    
    def list_plugins(self):
        """List all loaded plugins"""
        return list(self.loaded_plugins.keys())
    
    def process_command(self, command, context=None):
        """Process command through all plugins"""
        responses = []
        
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                response = plugin.process_command(command, context)
                if response:
                    responses.append(response)
            except Exception as e:
                logger.error(f"Error processing command in plugin {plugin_name}: {e}")
        
        return responses
    
    def cleanup(self):
        """Cleanup all plugins"""
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
        
        self.loaded_plugins.clear()
        self.plugin_configs.clear()
```

### **Plugin Manager CLI**

```python
# plugins/plugin_manager.py
import argparse
import sys
from plugin_loader import PluginLoader

def main():
    parser = argparse.ArgumentParser(description="Xiaozhi Plugin Manager")
    parser.add_argument("--list", action="store_true", help="List all plugins")
    parser.add_argument("--enable", help="Enable a plugin")
    parser.add_argument("--disable", help="Disable a plugin")
    parser.add_argument("--status", help="Get plugin status")
    parser.add_argument("--test", help="Test a plugin")
    
    args = parser.parse_args()
    
    loader = PluginLoader()
    
    if args.list:
        plugins = loader.list_plugins()
        print("Available plugins:")
        for plugin in plugins:
            print(f"  - {plugin}")
    
    elif args.enable:
        # Enable plugin logic
        print(f"Enabling plugin: {args.enable}")
    
    elif args.disable:
        # Disable plugin logic
        print(f"Disabling plugin: {args.disable}")
    
    elif args.status:
        plugin = loader.get_plugin(args.status)
        if plugin:
            status = plugin.get_status()
            print(f"Plugin {args.status} status: {status}")
        else:
            print(f"Plugin {args.status} not found")
    
    elif args.test:
        plugin = loader.get_plugin(args.test)
        if plugin:
            response = plugin.process_command("test")
            print(f"Plugin {args.test} test response: {response}")
        else:
            print(f"Plugin {args.test} not found")

if __name__ == "__main__":
    main()
```

## 📊 Plugin Monitoring

### **Plugin Health Monitoring**

```python
# plugins/plugin_monitor.py
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PluginMonitor:
    """Monitor plugin health and performance"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    def start_monitoring(self, plugin_loader):
        """Start monitoring plugins"""
        logger.info("Starting plugin monitoring...")
        
        while True:
            try:
                self._check_plugin_health(plugin_loader)
                self._check_plugin_performance(plugin_loader)
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Plugin monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error in plugin monitoring: {e}")
    
    def _check_plugin_health(self, plugin_loader):
        """Check plugin health"""
        for plugin_name, plugin in plugin_loader.loaded_plugins.items():
            try:
                status = plugin.get_status()
                if status.get('status') != 'running':
                    self._create_alert(plugin_name, f"Plugin status: {status.get('status')}")
            except Exception as e:
                self._create_alert(plugin_name, f"Health check failed: {e}")
    
    def _check_plugin_performance(self, plugin_loader):
        """Check plugin performance"""
        for plugin_name, plugin in plugin_loader.loaded_plugins.items():
            start_time = time.time()
            try:
                plugin.process_command("health_check")
                response_time = time.time() - start_time
                
                if response_time > 5.0:  # 5 second threshold
                    self._create_alert(plugin_name, f"Slow response time: {response_time:.2f}s")
                
                # Store metrics
                if plugin_name not in self.metrics:
                    self.metrics[plugin_name] = []
                self.metrics[plugin_name].append({
                    'timestamp': datetime.now(),
                    'response_time': response_time
                })
                
            except Exception as e:
                self._create_alert(plugin_name, f"Performance check failed: {e}")
    
    def _create_alert(self, plugin_name, message):
        """Create alert"""
        alert = {
            'timestamp': datetime.now(),
            'plugin': plugin_name,
            'message': message,
            'severity': 'warning'
        }
        self.alerts.append(alert)
        logger.warning(f"Plugin alert: {plugin_name} - {message}")
    
    def get_metrics(self, plugin_name=None):
        """Get plugin metrics"""
        if plugin_name:
            return self.metrics.get(plugin_name, [])
        return self.metrics
    
    def get_alerts(self, plugin_name=None):
        """Get plugin alerts"""
        if plugin_name:
            return [alert for alert in self.alerts if alert['plugin'] == plugin_name]
        return self.alerts
```

## 🎯 Plugin Examples

### **Weather Plugin**

```python
# plugins/weather_plugin/weather_plugin.py
from plugins.base.plugin import BasePlugin
import requests
import json

class WeatherPlugin(BasePlugin):
    """Weather information plugin"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.default_location = config.get('default_location', 'New York, NY')
        self.units = config.get('units', 'metric')
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def initialize(self):
        """Initialize weather plugin"""
        if not self.api_key:
            raise ValueError("Weather API key is required")
        
        self.logger.info("Weather plugin initialized")
    
    def process_command(self, command, context=None):
        """Process weather commands"""
        command_lower = command.lower()
        
        if "weather" in command_lower:
            return self._get_current_weather()
        elif "forecast" in command_lower:
            return self._get_forecast()
        elif "temperature" in command_lower:
            return self._get_temperature()
        else:
            return "I can help with weather information. Ask me about current weather, forecast, or temperature."
    
    def _get_current_weather(self):
        """Get current weather"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': self.default_location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            
            return f"Current weather in {self.default_location}: {weather}, {temp}°C, humidity {humidity}%"
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Weather API error: {e}")
            return "Sorry, I couldn't get the weather information."
    
    def _get_forecast(self):
        """Get weather forecast"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': self.default_location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast = data['list'][0]  # Next 3 hours
            weather = forecast['weather'][0]['description']
            temp = forecast['main']['temp']
            time = forecast['dt_txt']
            
            return f"Weather forecast for {time}: {weather}, {temp}°C"
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Weather forecast API error: {e}")
            return "Sorry, I couldn't get the weather forecast."
    
    def _get_temperature(self):
        """Get current temperature"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': self.default_location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            
            return f"Current temperature in {self.default_location}: {temp}°C (feels like {feels_like}°C)"
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Temperature API error: {e}")
            return "Sorry, I couldn't get the temperature information."
    
    def get_status(self):
        """Get plugin status"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "status": "running" if self.enabled else "disabled",
            "api_connected": bool(self.api_key)
        }
```

### **News Plugin**

```python
# plugins/news_plugin/news_plugin.py
from plugins.base.plugin import BasePlugin
import requests
import json

class NewsPlugin(BasePlugin):
    """News information plugin"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.sources = config.get('sources', ['bbc-news', 'cnn'])
        self.max_articles = config.get('max_articles', 5)
        self.base_url = "https://newsapi.org/v2"
    
    def initialize(self):
        """Initialize news plugin"""
        if not self.api_key:
            raise ValueError("News API key is required")
        
        self.logger.info("News plugin initialized")
    
    def process_command(self, command, context=None):
        """Process news commands"""
        command_lower = command.lower()
        
        if "news" in command_lower:
            return self._get_latest_news()
        elif "headlines" in command_lower:
            return self._get_headlines()
        elif "breaking" in command_lower:
            return self._get_breaking_news()
        else:
            return "I can help with news information. Ask me about latest news, headlines, or breaking news."
    
    def _get_latest_news(self):
        """Get latest news"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                'sources': ','.join(self.sources),
                'apiKey': self.api_key,
                'pageSize': self.max_articles,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data['articles']
            if not articles:
                return "No news articles found."
            
            news_summary = "Latest news:\n"
            for i, article in enumerate(articles[:3], 1):
                title = article['title']
                source = article['source']['name']
                news_summary += f"{i}. {title} ({source})\n"
            
            return news_summary
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"News API error: {e}")
            return "Sorry, I couldn't get the latest news."
    
    def _get_headlines(self):
        """Get news headlines"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'sources': ','.join(self.sources),
                'apiKey': self.api_key,
                'pageSize': self.max_articles
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data['articles']
            if not articles:
                return "No headlines found."
            
            headlines = "Top headlines:\n"
            for i, article in enumerate(articles[:3], 1):
                title = article['title']
                headlines += f"{i}. {title}\n"
            
            return headlines
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Headlines API error: {e}")
            return "Sorry, I couldn't get the headlines."
    
    def _get_breaking_news(self):
        """Get breaking news"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'sources': ','.join(self.sources),
                'apiKey': self.api_key,
                'pageSize': 3,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data['articles']
            if not articles:
                return "No breaking news found."
            
            breaking_news = "Breaking news:\n"
            for i, article in enumerate(articles, 1):
                title = article['title']
                breaking_news += f"{i}. {title}\n"
            
            return breaking_news
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Breaking news API error: {e}")
            return "Sorry, I couldn't get the breaking news."
    
    def get_status(self):
        """Get plugin status"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "status": "running" if self.enabled else "disabled",
            "api_connected": bool(self.api_key),
            "sources": self.sources
        }
```

## 🎯 Next Steps

After setting up plugins:

1. **[Test Plugin Functionality](../features/voice-interaction.md)** - Verify plugins work correctly
2. **[Create Custom Plugins](../guides/custom-plugins.md)** - Build your own plugins
3. **[Plugin Management](../configuration/advanced.md)** - Advanced plugin configuration
4. **[Monitor Plugin Performance](../guides/monitoring.md)** - Track plugin health

## 🆘 Need Help?

- **Plugin Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Plugin Development?** See [Custom Plugins](../guides/custom-plugins.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Plugin Structure**
```
plugins/
├── __init__.py
├── base/
│   └── plugin.py
├── my_plugin/
│   ├── __init__.py
│   ├── my_plugin.py
│   └── config.yaml
```

### **Plugin Methods**
- `initialize()` - Initialize plugin
- `process_command()` - Process voice commands
- `get_status()` - Get plugin status
- `cleanup()` - Cleanup resources

### **Configuration**
```yaml
plugins:
  enabled: true
  plugin_dir: plugins/
  auto_load: true
```

---

**Your plugin system is ready! 🎉**

👉 **[Next: API Reference →](api.md)**
