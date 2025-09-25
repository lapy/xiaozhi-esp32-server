# 📡 Communication Protocols

This guide documents the communication protocols used by Xiaozhi ESP32 Server for device communication, data exchange, and system integration.

## 🎯 Protocol Overview

Xiaozhi uses several communication protocols:
- **WebSocket Protocol** - Real-time communication with ESP32 devices
- **HTTP/HTTPS Protocol** - REST API and OTA updates
- **MQTT Protocol** - IoT device communication
- **Serial Protocol** - Direct device communication
- **Audio Protocol** - Audio data transmission

## 🔌 WebSocket Protocol

### **Connection Establishment**

```javascript
// WebSocket connection URL
ws://YOUR_IP:8000/xiaozhi/v1/

// Secure WebSocket (for 4G mode)
wss://YOUR_DOMAIN:8000/xiaozhi/v1/
```

### **Handshake Process**

1. **Client connects** to WebSocket endpoint
2. **Server accepts** connection
3. **Device registration** message sent
4. **Server confirms** registration
5. **Communication begins**

### **Message Format**

All WebSocket messages use JSON format with the following structure:

```json
{
    "type": "message_type",
    "data": {
        "key": "value"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "device_id": "esp32_device_001",
    "message_id": "msg_123456"
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
        "capabilities": ["audio_input", "audio_output", "wifi"],
        "hardware_info": {
            "chip_model": "ESP32-S3",
            "chip_revision": "0",
            "cpu_freq": 240,
            "flash_size": 16777216,
            "psram_size": 8388608
        }
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### **Audio Data Transmission**
```json
{
    "type": "audio_data",
    "data": {
        "device_id": "esp32_device_001",
        "audio_format": "wav",
        "sample_rate": 16000,
        "channels": 1,
        "bit_depth": 16,
        "duration_ms": 1500,
        "data": "base64_encoded_audio_data",
        "compression": "none"
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### **Voice Command Processing**
```json
{
    "type": "voice_command",
    "data": {
        "device_id": "esp32_device_001",
        "command": "turn on the living room light",
        "confidence": 0.95,
        "language": "en",
        "processing_time_ms": 1200,
        "audio_duration_ms": 1500
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### **Response Delivery**
```json
{
    "type": "response",
    "data": {
        "device_id": "esp32_device_001",
        "text": "I'll turn on the living room light for you.",
        "audio_url": "http://YOUR_IP:8000/audio/response_123.wav",
        "audio_data": "base64_encoded_audio_data",
        "actions": [
            {
                "type": "homeassistant",
                "action": "turn_on",
                "entity_id": "light.living_room",
                "parameters": {}
            }
        ],
        "processing_time_ms": 2500
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### **Error Handling**
```json
{
    "type": "error",
    "data": {
        "device_id": "esp32_device_001",
        "error_code": "AUDIO_PROCESSING_FAILED",
        "error_message": "Failed to process audio data",
        "details": {
            "reason": "Invalid audio format",
            "expected_format": "wav",
            "received_format": "mp3"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

#### **Heartbeat/Ping**
```json
{
    "type": "ping",
    "data": {
        "device_id": "esp32_device_001",
        "uptime": 3600,
        "memory_usage": 65,
        "cpu_usage": 45,
        "wifi_signal": -45,
        "free_heap": 204800
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### **WebSocket Frame Format**

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
```

## 🌐 HTTP/HTTPS Protocol

### **REST API Endpoints**

#### **Base URL Structure**
```
http://YOUR_IP:8000/api/v1/
https://YOUR_DOMAIN:8000/api/v1/  # For secure connections
```

#### **Authentication Headers**
```
X-API-Key: your-api-key
Authorization: Bearer your-jwt-token
Content-Type: application/json
```

#### **Standard HTTP Methods**
- **GET** - Retrieve data
- **POST** - Create new resources
- **PUT** - Update existing resources
- **DELETE** - Remove resources
- **PATCH** - Partial updates

### **Request/Response Format**

#### **Standard Response Structure**
```json
{
    "success": true,
    "data": {
        "key": "value"
    },
    "message": "Operation completed successfully",
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456"
}
```

#### **Error Response Structure**
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
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456"
}
```

### **Content Types**

#### **JSON Content**
```
Content-Type: application/json
```

#### **Multipart Form Data**
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
```

#### **Audio Content**
```
Content-Type: audio/wav
Content-Type: audio/mpeg
Content-Type: audio/ogg
```

## 📡 MQTT Protocol

### **Connection Parameters**

```yaml
mqtt:
  broker: mqtt://broker.hivemq.com:1883
  username: your-username
  password: your-password
  client_id: xiaozhi_device_001
  keepalive: 60
  clean_session: true
  qos: 1
```

### **Topic Structure**

#### **Command Topics**
```
xiaozhi/commands/{device_id}
xiaozhi/commands/broadcast
xiaozhi/commands/group/{group_id}
```

#### **Status Topics**
```
xiaozhi/status/{device_id}
xiaozhi/status/broadcast
xiaozhi/status/group/{group_id}
```

#### **Sensor Topics**
```
xiaozhi/sensors/{device_id}/{sensor_type}
xiaozhi/sensors/{device_id}/temperature
xiaozhi/sensors/{device_id}/humidity
xiaozhi/sensors/{device_id}/audio_level
```

#### **Event Topics**
```
xiaozhi/events/{device_id}
xiaozhi/events/voice_command
xiaozhi/events/device_connected
xiaozhi/events/device_disconnected
```

### **Message Format**

#### **Command Message**
```json
{
    "command": "turn_on_light",
    "parameters": {
        "entity_id": "light.living_room",
        "brightness": 255
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "device_id": "esp32_device_001"
}
```

#### **Status Message**
```json
{
    "status": "connected",
    "uptime": 3600,
    "memory_usage": 65,
    "cpu_usage": 45,
    "wifi_signal": -45,
    "timestamp": "2024-01-01T00:00:00Z",
    "device_id": "esp32_device_001"
}
```

#### **Sensor Message**
```json
{
    "sensor_type": "temperature",
    "value": 22.5,
    "unit": "celsius",
    "timestamp": "2024-01-01T00:00:00Z",
    "device_id": "esp32_device_001"
}
```

### **QoS Levels**

- **QoS 0** - At most once delivery (fire and forget)
- **QoS 1** - At least once delivery (acknowledged)
- **QoS 2** - Exactly once delivery (assured)

## 🔌 Serial Protocol

### **Serial Communication Parameters**

```yaml
serial:
  port: /dev/ttyUSB0
  baudrate: 115200
  bytesize: 8
  parity: N
  stopbits: 1
  timeout: 1
  xonxoff: false
  rtscts: false
  dsrdtr: false
```

### **Message Format**

#### **Command Format**
```
<START><LENGTH><COMMAND><PARAMETERS><CHECKSUM><END>
```

#### **Response Format**
```
<START><LENGTH><STATUS><DATA><CHECKSUM><END>
```

#### **Example Commands**
```
# Turn on LED
$LED,ON,255#

# Set volume
$VOL,80#

# Get status
$STA?#

# Reset device
$RST#
```

### **Error Codes**

| Code | Description |
|------|-------------|
| `OK` | Command successful |
| `ERR` | General error |
| `PARAM` | Invalid parameter |
| `TIMEOUT` | Command timeout |
| `BUSY` | Device busy |
| `UNKNOWN` | Unknown command |

## 🎵 Audio Protocol

### **Audio Format Specifications**

#### **Input Audio (Microphone)**
```yaml
input_audio:
  format: wav
  sample_rate: 16000
  channels: 1
  bit_depth: 16
  encoding: pcm
  endianness: little
  compression: none
```

#### **Output Audio (Speaker)**
```yaml
output_audio:
  format: wav
  sample_rate: 22050
  channels: 1
  bit_depth: 16
  encoding: pcm
  endianness: little
  compression: none
```

### **Audio Data Transmission**

#### **Raw Audio Data**
```
[Header][Audio Data][Footer]
```

#### **Header Format**
```
Offset  Size  Description
0       4     Magic number (0x52494646)
4       4     File size
8       4     Format (0x57415645)
12      4     Subchunk1 size
16      2     Audio format (1 = PCM)
18      2     Number of channels
20      4     Sample rate
24      4     Byte rate
28      2     Block align
30      2     Bits per sample
```

#### **Compressed Audio**
```yaml
compressed_audio:
  format: mp3
  bitrate: 128kbps
  sample_rate: 22050
  channels: 1
  compression: mp3
  quality: standard
```

### **Audio Streaming Protocol**

#### **Streaming Header**
```json
{
    "stream_id": "stream_123456",
    "format": "wav",
    "sample_rate": 16000,
    "channels": 1,
    "bit_depth": 16,
    "chunk_size": 1024,
    "total_chunks": 10
}
```

#### **Audio Chunk**
```json
{
    "stream_id": "stream_123456",
    "chunk_number": 1,
    "chunk_data": "base64_encoded_audio_data",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔐 Security Protocols

### **TLS/SSL Configuration**

#### **TLS Version**
```
TLS 1.2 or higher
```

#### **Cipher Suites**
```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

#### **Certificate Requirements**
```
- Valid SSL certificate
- Chain of trust
- Proper domain validation
- Minimum 2048-bit RSA or 256-bit ECDSA
```

### **Authentication Protocols**

#### **API Key Authentication**
```
Header: X-API-Key: your-api-key
```

#### **JWT Token Authentication**
```
Header: Authorization: Bearer your-jwt-token
```

#### **OAuth 2.0**
```
Authorization: Bearer access_token
```

### **Data Encryption**

#### **Transport Encryption**
```
- TLS 1.2+ for HTTP/HTTPS
- WSS for WebSocket
- MQTT over TLS
```

#### **Data Encryption**
```
- AES-256-GCM for sensitive data
- AES-128-CBC for audio data
- RSA-2048 for key exchange
```

## 📊 Protocol Performance

### **WebSocket Performance**

| Metric | Value |
|--------|-------|
| **Connection Time** | < 100ms |
| **Message Latency** | < 50ms |
| **Throughput** | 1000 msg/s |
| **Concurrent Connections** | 100+ |

### **HTTP Performance**

| Metric | Value |
|--------|-------|
| **Response Time** | < 200ms |
| **Throughput** | 500 req/s |
| **Concurrent Requests** | 50+ |
| **Payload Size** | 1MB max |

### **MQTT Performance**

| Metric | Value |
|--------|-------|
| **Connection Time** | < 200ms |
| **Message Latency** | < 100ms |
| **Throughput** | 10000 msg/s |
| **Concurrent Connections** | 1000+ |

## 🛠️ Protocol Implementation

### **WebSocket Client (JavaScript)**

```javascript
class XiaozhiWebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('Connected to Xiaozhi WebSocket');
                this.reconnectAttempts = 0;
                this.registerDevice();
            };
            
            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket connection closed');
                this.reconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.reconnect();
        }
    }
    
    registerDevice() {
        const message = {
            type: 'device_register',
            data: {
                device_id: 'web_client_001',
                device_type: 'web',
                firmware_version: '1.0.0',
                capabilities: ['audio_input', 'audio_output']
            },
            timestamp: new Date().toISOString()
        };
        
        this.send(message);
    }
    
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'response':
                console.log('Response:', message.data.text);
                break;
            case 'error':
                console.error('Error:', message.data.error_message);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => this.connect(), this.reconnectInterval);
        }
    }
}

// Usage
const client = new XiaozhiWebSocketClient('ws://YOUR_IP:8000/xiaozhi/v1/');
client.connect();
```

### **MQTT Client (Python)**

```python
import paho.mqtt.client as mqtt
import json
import time

class XiaozhiMQTTClient:
    def __init__(self, broker, port, username, password):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client = mqtt.Client()
        self.device_id = "esp32_device_001"
        
    def connect(self):
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            self.subscribe_to_topics()
            self.publish_status()
        else:
            print(f"Failed to connect: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload.decode())
            self.handle_command(message)
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker")
    
    def subscribe_to_topics(self):
        topics = [
            f"xiaozhi/commands/{self.device_id}",
            "xiaozhi/commands/broadcast"
        ]
        
        for topic in topics:
            self.client.subscribe(topic)
            print(f"Subscribed to {topic}")
    
    def publish_status(self):
        status = {
            "status": "connected",
            "uptime": int(time.time()),
            "memory_usage": 65,
            "cpu_usage": 45,
            "wifi_signal": -45,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "device_id": self.device_id
        }
        
        topic = f"xiaozhi/status/{self.device_id}"
        self.client.publish(topic, json.dumps(status))
        print(f"Published status to {topic}")
    
    def handle_command(self, command):
        print(f"Received command: {command}")
        
        # Process command here
        if command.get("command") == "turn_on_light":
            entity_id = command.get("parameters", {}).get("entity_id")
            print(f"Turning on light: {entity_id}")
            
            # Send response
            response = {
                "command": "turn_on_light",
                "status": "success",
                "entity_id": entity_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            topic = f"xiaozhi/status/{self.device_id}"
            self.client.publish(topic, json.dumps(response))

# Usage
client = XiaozhiMQTTClient("broker.hivemq.com", 1883, "username", "password")
client.connect()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.client.disconnect()
```

## 🎯 Next Steps

After understanding the protocols:

1. **[Test Voice Interaction](../features/voice-interaction.md)** - Use the protocols for voice commands
2. **[Create Custom Integrations](../features/integrations.md)** - Build protocol-based integrations
3. **[Monitor Performance](../guides/monitoring.md)** - Track protocol performance
4. **[Troubleshoot Issues](../support/troubleshooting.md)** - Fix protocol-related problems

## 🆘 Need Help?

- **Protocol Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Security Concerns?** See [Security Guide](../guides/security.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Protocol URLs**
- **WebSocket**: `ws://YOUR_IP:8000/xiaozhi/v1/`
- **REST API**: `http://YOUR_IP:8000/api/v1/`
- **MQTT**: `mqtt://broker.hivemq.com:1883`

### **Message Format**
```json
{
    "type": "message_type",
    "data": {},
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Common Commands**
- **Device Register**: `{"type": "device_register", "data": {...}}`
- **Audio Data**: `{"type": "audio_data", "data": {...}}`
- **Voice Command**: `{"type": "voice_command", "data": {...}}`

---

**Your communication protocols reference is ready! 🎉**

👉 **[Next: Changelog →](changelog.md)**
