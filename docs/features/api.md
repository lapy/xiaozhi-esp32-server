# 📚 API Reference

This guide provides comprehensive documentation for the Xiaozhi ESP32 Server API, including endpoints, parameters, responses, and examples.

## 🎯 API Overview

The Xiaozhi ESP32 Server provides several APIs:
- **WebSocket API** - Real-time communication with ESP32 devices
- **REST API** - HTTP endpoints for configuration and management
- **OTA API** - Over-the-air firmware updates
- **Plugin API** - Extend functionality with custom plugins

## 🔌 WebSocket API

### **Connection**

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://YOUR_IP:8000/xiaozhi/v1/');

ws.onopen = function() {
    console.log('Connected to Xiaozhi WebSocket');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function() {
    console.log('WebSocket connection closed');
};
```

### **Message Format**

All WebSocket messages use JSON format:

```json
{
    "type": "message_type",
    "data": {
        "key": "value"
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Message Types**

#### **Device Registration**
```json
{
    "type": "device_register",
    "data": {
        "device_id": "esp32_device_001",
        "device_type": "esp32s3",
        "firmware_version": "1.0.0",
        "capabilities": ["audio_input", "audio_output", "wifi"]
    }
}
```

#### **Audio Data**
```json
{
    "type": "audio_data",
    "data": {
        "device_id": "esp32_device_001",
        "audio_format": "wav",
        "sample_rate": 16000,
        "channels": 1,
        "data": "base64_encoded_audio_data"
    }
}
```

#### **Voice Command**
```json
{
    "type": "voice_command",
    "data": {
        "device_id": "esp32_device_001",
        "command": "turn on the living room light",
        "confidence": 0.95,
        "language": "en"
    }
}
```

#### **Response**
```json
{
    "type": "response",
    "data": {
        "device_id": "esp32_device_001",
        "text": "I'll turn on the living room light for you.",
        "audio_url": "http://YOUR_IP:8000/audio/response_123.wav",
        "actions": [
            {
                "type": "homeassistant",
                "action": "turn_on",
                "entity_id": "light.living_room"
            }
        ]
    }
}
```

#### **Error**
```json
{
    "type": "error",
    "data": {
        "device_id": "esp32_device_001",
        "error_code": "AUDIO_PROCESSING_FAILED",
        "error_message": "Failed to process audio data",
        "details": {
            "reason": "Invalid audio format"
        }
    }
}
```

## 🌐 REST API

### **Base URL**
```
http://YOUR_IP:8000/api/v1/
```

### **Authentication**

Most endpoints require API key authentication:

```bash
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     http://YOUR_IP:8000/api/v1/endpoint
```

### **Endpoints**

#### **GET /devices**
Get list of connected devices.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/devices
```

**Response:**
```json
{
    "devices": [
        {
            "device_id": "esp32_device_001",
            "device_type": "esp32s3",
            "firmware_version": "1.0.0",
            "status": "connected",
            "last_seen": "2024-01-01T00:00:00Z",
            "capabilities": ["audio_input", "audio_output", "wifi"]
        }
    ],
    "total": 1
}
```

#### **GET /devices/{device_id}**
Get specific device information.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/devices/esp32_device_001
```

**Response:**
```json
{
    "device_id": "esp32_device_001",
    "device_type": "esp32s3",
    "firmware_version": "1.0.0",
    "status": "connected",
    "last_seen": "2024-01-01T00:00:00Z",
    "capabilities": ["audio_input", "audio_output", "wifi"],
    "configuration": {
        "wake_word": "hey xiaozhi",
        "language": "en",
        "volume": 0.8
    }
}
```

#### **POST /devices/{device_id}/command**
Send command to specific device.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"command": "turn on the living room light"}' \
     http://YOUR_IP:8000/api/v1/devices/esp32_device_001/command
```

**Response:**
```json
{
    "success": true,
    "message": "Command sent successfully",
    "command_id": "cmd_123456"
}
```

#### **GET /devices/{device_id}/status**
Get device status and health.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/devices/esp32_device_001/status
```

**Response:**
```json
{
    "device_id": "esp32_device_001",
    "status": "connected",
    "health": "good",
    "uptime": 3600,
    "memory_usage": 65,
    "cpu_usage": 45,
    "wifi_signal": -45,
    "last_command": "2024-01-01T00:00:00Z"
}
```

#### **POST /audio/process**
Process audio data and get response.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: multipart/form-data" \
     -F "audio=@audio_file.wav" \
     -F "device_id=esp32_device_001" \
     http://YOUR_IP:8000/api/v1/audio/process
```

**Response:**
```json
{
    "success": true,
    "transcription": "turn on the living room light",
    "response": "I'll turn on the living room light for you.",
    "audio_url": "http://YOUR_IP:8000/audio/response_123.wav",
    "processing_time": 1.5
}
```

#### **GET /config**
Get current configuration.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/config
```

**Response:**
```json
{
    "server": {
        "websocket": "ws://YOUR_IP:8000/xiaozhi/v1/",
        "ota": "http://YOUR_IP:8003/xiaozhi/ota/"
    },
    "selected_module": {
        "VAD": "SileroVAD",
        "ASR": "WhisperASR",
        "LLM": "LMStudioLLM",
        "TTS": "EdgeTTS"
    },
    "plugins": {
        "enabled": true,
        "loaded_plugins": ["weather", "news", "homeassistant"]
    }
}
```

#### **PUT /config**
Update configuration.

**Request:**
```bash
curl -X PUT \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"selected_module": {"ASR": "OpenAIASR"}}' \
     http://YOUR_IP:8000/api/v1/config
```

**Response:**
```json
{
    "success": true,
    "message": "Configuration updated successfully",
    "restart_required": true
}
```

## 📡 OTA API

### **Base URL**
```
http://YOUR_IP:8003/xiaozhi/ota/
```

### **Endpoints**

#### **GET /**
Get OTA interface status.

**Request:**
```bash
curl http://YOUR_IP:8003/xiaozhi/ota/
```

**Response:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Xiaozhi OTA Interface</title>
</head>
<body>
    <h1>OTA interface is running normally</h1>
    <p>Websocket address sent to the device is: ws://YOUR_IP:8000/xiaozhi/v1/</p>
</body>
</html>
```

#### **GET /firmware**
Get available firmware versions.

**Request:**
```bash
curl http://YOUR_IP:8003/xiaozhi/ota/firmware
```

**Response:**
```json
{
    "firmware_versions": [
        {
            "version": "1.0.0",
            "release_date": "2024-01-01",
            "download_url": "http://YOUR_IP:8003/xiaozhi/ota/firmware/1.0.0.bin",
            "size": 1048576,
            "checksum": "sha256:abc123..."
        }
    ],
    "latest_version": "1.0.0"
}
```

#### **POST /firmware/upload**
Upload new firmware.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -F "firmware=@firmware.bin" \
     -F "version=1.0.1" \
     http://YOUR_IP:8003/xiaozhi/ota/firmware/upload
```

**Response:**
```json
{
    "success": true,
    "message": "Firmware uploaded successfully",
    "version": "1.0.1",
    "download_url": "http://YOUR_IP:8003/xiaozhi/ota/firmware/1.0.1.bin"
}
```

## 🔌 Plugin API

### **Plugin Management**

#### **GET /plugins**
Get list of available plugins.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/plugins
```

**Response:**
```json
{
    "plugins": [
        {
            "name": "weather",
            "version": "1.0.0",
            "enabled": true,
            "status": "running",
            "description": "Weather information plugin"
        },
        {
            "name": "news",
            "version": "1.0.0",
            "enabled": true,
            "status": "running",
            "description": "News information plugin"
        }
    ]
}
```

#### **POST /plugins/{plugin_name}/enable**
Enable a plugin.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/plugins/weather/enable
```

**Response:**
```json
{
    "success": true,
    "message": "Plugin enabled successfully"
}
```

#### **POST /plugins/{plugin_name}/disable**
Disable a plugin.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/plugins/weather/disable
```

**Response:**
```json
{
    "success": true,
    "message": "Plugin disabled successfully"
}
```

#### **POST /plugins/{plugin_name}/command**
Send command to plugin.

**Request:**
```bash
curl -X POST \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"command": "get weather"}' \
     http://YOUR_IP:8000/api/v1/plugins/weather/command
```

**Response:**
```json
{
    "success": true,
    "response": "Current weather: Sunny, 25°C",
    "plugin": "weather"
}
```

## 📊 Monitoring API

### **System Status**

#### **GET /status**
Get system status and health.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/status
```

**Response:**
```json
{
    "status": "running",
    "uptime": 3600,
    "version": "1.0.0",
    "components": {
        "websocket": "running",
        "rest_api": "running",
        "ota": "running",
        "plugins": "running"
    },
    "metrics": {
        "active_connections": 5,
        "total_requests": 1000,
        "average_response_time": 1.5,
        "memory_usage": 65,
        "cpu_usage": 45
    }
}
```

#### **GET /metrics**
Get detailed metrics.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/metrics
```

**Response:**
```json
{
    "timestamp": "2024-01-01T00:00:00Z",
    "metrics": {
        "requests_total": 1000,
        "requests_per_second": 10,
        "average_response_time": 1.5,
        "error_rate": 0.01,
        "active_connections": 5,
        "memory_usage": {
            "total": 8192,
            "used": 5324,
            "free": 2868
        },
        "cpu_usage": {
            "user": 30,
            "system": 15,
            "idle": 55
        }
    }
}
```

## 🔐 Authentication

### **API Key Authentication**

All API endpoints require authentication via API key:

```bash
# Set API key in header
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/endpoint

# Or use query parameter
curl "http://YOUR_IP:8000/api/v1/endpoint?api_key=your-api-key"
```

### **JWT Token Authentication**

For advanced authentication, use JWT tokens:

```bash
# Get JWT token
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}' \
     http://YOUR_IP:8000/api/v1/auth/login

# Use JWT token
curl -H "Authorization: Bearer your-jwt-token" \
     http://YOUR_IP:8000/api/v1/endpoint
```

## 📝 Error Handling

### **Error Response Format**

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "field": "Additional error details"
        }
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Common Error Codes**

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_API_KEY` | Invalid or missing API key | 401 |
| `DEVICE_NOT_FOUND` | Device not found | 404 |
| `PLUGIN_NOT_FOUND` | Plugin not found | 404 |
| `INVALID_REQUEST` | Invalid request format | 400 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Internal server error | 500 |

### **Error Handling Example**

```javascript
fetch('/api/v1/devices')
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => {
                throw new Error(error.error.message);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Devices:', data);
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
```

## 🧪 Testing the API

### **Using curl**

```bash
# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
     http://YOUR_IP:8000/xiaozhi/v1/

# Test REST API
curl -H "X-API-Key: your-api-key" \
     http://YOUR_IP:8000/api/v1/status

# Test OTA API
curl http://YOUR_IP:8003/xiaozhi/ota/
```

### **Using Python**

```python
import requests
import websocket
import json

# Test REST API
def test_rest_api():
    headers = {'X-API-Key': 'your-api-key'}
    response = requests.get('http://YOUR_IP:8000/api/v1/status', headers=headers)
    print(response.json())

# Test WebSocket
def test_websocket():
    def on_message(ws, message):
        data = json.loads(message)
        print('Received:', data)
    
    def on_error(ws, error):
        print('Error:', error)
    
    def on_close(ws):
        print('Connection closed')
    
    def on_open(ws):
        print('Connected')
        # Send test message
        ws.send(json.dumps({
            'type': 'device_register',
            'data': {
                'device_id': 'test_device',
                'device_type': 'esp32s3',
                'firmware_version': '1.0.0'
            }
        }))
    
    ws = websocket.WebSocketApp('ws://YOUR_IP:8000/xiaozhi/v1/',
                               on_message=on_message,
                               on_error=on_error,
                               on_close=on_close,
                               on_open=on_open)
    ws.run_forever()

# Run tests
test_rest_api()
test_websocket()
```

### **Using JavaScript**

```javascript
// Test REST API
async function testRestAPI() {
    try {
        const response = await fetch('http://YOUR_IP:8000/api/v1/status', {
            headers: {
                'X-API-Key': 'your-api-key'
            }
        });
        const data = await response.json();
        console.log('Status:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Test WebSocket
function testWebSocket() {
    const ws = new WebSocket('ws://YOUR_IP:8000/xiaozhi/v1/');
    
    ws.onopen = function() {
        console.log('Connected');
        // Send test message
        ws.send(JSON.stringify({
            type: 'device_register',
            data: {
                device_id: 'test_device',
                device_type: 'esp32s3',
                firmware_version: '1.0.0'
            }
        }));
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    };
    
    ws.onerror = function(error) {
        console.error('Error:', error);
    };
    
    ws.onclose = function() {
        console.log('Connection closed');
    };
}

// Run tests
testRestAPI();
testWebSocket();
```

## 🎯 Next Steps

After understanding the API:

1. **[Test Voice Interaction](../features/voice-interaction.md)** - Use the API for voice commands
2. **[Create Custom Integrations](../features/integrations.md)** - Build API-based integrations
3. **[Develop Plugins](../features/plugins.md)** - Use the Plugin API
4. **[Monitor Performance](../guides/monitoring.md)** - Use the Monitoring API

## 🆘 Need Help?

- **API Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Authentication Problems?** See [Security Guide](../guides/security.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **API Endpoints**
- **WebSocket**: `ws://YOUR_IP:8000/xiaozhi/v1/`
- **REST API**: `http://YOUR_IP:8000/api/v1/`
- **OTA API**: `http://YOUR_IP:8003/xiaozhi/ota/`

### **Authentication**
- **API Key**: `X-API-Key: your-api-key`
- **JWT Token**: `Authorization: Bearer your-jwt-token`

### **Common Commands**
```bash
# Get status
curl -H "X-API-Key: your-api-key" http://YOUR_IP:8000/api/v1/status

# List devices
curl -H "X-API-Key: your-api-key" http://YOUR_IP:8000/api/v1/devices

# Send command
curl -X POST -H "X-API-Key: your-api-key" \
     -d '{"command": "hello"}' \
     http://YOUR_IP:8000/api/v1/devices/device_id/command
```

---

**Your API reference is ready! 🎉**

👉 **[Next: Communication Protocols →](../reference/protocols.md)**
