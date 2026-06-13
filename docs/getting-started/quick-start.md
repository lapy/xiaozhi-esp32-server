# ⚡ Quick Start Guide

Get Xiaozhi ESP32 Server up and running in just 5 minutes! This guide will have you talking to your ESP32 device in no time.

## 🎯 What We'll Build

By the end of this guide, you'll have:
- ✅ Xiaozhi server running locally
- ✅ ESP32 device connected and configured
- ✅ Voice interaction working
- ✅ Basic voice commands responding

## 🚀 Step 1: Start the Server (2 minutes)

### **Option A: Docker (Recommended)**

```bash
# Clone the repository
git clone https://github.com/lapy/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server

# Start with Docker Compose
docker-compose up -d
```

### **Option B: Local Installation**

```bash
# Clone the repository
git clone https://github.com/lapy/xiaozhi-esp32-server.git
cd xiaozhi-esp32-server

# Install dependencies
cd main/xiaozhi-server
pip install -r requirements.txt

# Start the server
python app.py
```

### **✅ Verify Server is Running**

Open your browser and go to:
- **Web Interface**: http://localhost:8001
- **OTA Interface**: http://localhost:8003/xiaozhi/ota/

You should see the Xiaozhi management interface!

## 🔧 Step 2: Configure AI Providers (1 minute)

### **Quick Configuration**

1. **Open the web interface**: http://localhost:8001
2. **Register** your first admin account
3. **Go to Model Configuration** → **Large Language Model**
4. **Configure OpenAI** (or use free alternatives):

```yaml
# For OpenAI (requires API key)
LLM_OpenAILLM:
  api_key: your_openai_api_key_here
  model_name: gpt-4o-mini

# For free local setup
LLM_LMStudioLLM:
  base_url: http://localhost:1234/v1
  model_name: llama3.1:8b
```

### **Free Alternative Setup**

If you don't have OpenAI API access, use the free local setup:

```bash
# Install LMStudio
# Download from: https://lmstudio.ai

# Start LMStudio and load a model
# Use the local API endpoint: http://localhost:1234/v1
```

## 🔌 Step 3: Prepare Your ESP32 (1 minute)

### **Download Firmware**

1. **Go to OTA interface**: http://localhost:8003/xiaozhi/ota/
2. **Copy the WebSocket URL**: `ws://YOUR_IP:8000/xiaozhi/v1/`
3. **Download firmware** for your ESP32 board

### **Flash Your ESP32**

#### **Method 1: Web-based Flashing**
1. **Go to**: [ESP-Launchpad](https://espressif.github.io/esp-launchpad/)
2. **Upload firmware** file
3. **Connect ESP32** via USB
4. **Flash** the firmware

#### **Method 2: Command Line**
```bash
# Install esptool
pip install esptool

# Flash firmware
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 firmware.bin
```

## 🎤 Step 4: Connect and Test (1 minute)

### **Connect Your ESP32**

1. **Power on** your ESP32 device
2. **Wait for connection** (LED should indicate connection)
3. **Check OTA interface** for device status

### **Test Voice Interaction**

1. **Say**: "Hello Xiaozhi"
2. **Wait for response** (should hear synthesized speech)
3. **Try commands**:
   - "What's the weather?"
   - "Tell me a joke"
   - "What time is it?"

## 🎉 Success! What's Next?

### **🎯 Try These Commands**

- **"Hello"** - Basic greeting
- **"What's the weather?"** - Weather information
- **"Tell me a joke"** - Entertainment
- **"What time is it?"** - Time and date
- **"Help"** - List available commands

### **🔧 Customize Your Setup**

1. **Add more AI providers** in the web interface
2. **Configure custom responses** in agent settings
3. **Set up integrations** with HomeAssistant or MQTT
4. **Create custom plugins** for specific functionality

## 🛠️ Troubleshooting

### **Server Won't Start**

```bash
# Check Docker status
docker ps

# Check logs
docker logs xiaozhi-esp32-server

# Restart if needed
docker-compose restart
```

### **ESP32 Won't Connect**

1. **Check WebSocket URL** in OTA interface
2. **Verify network** connection
3. **Check firewall** settings
4. **Restart ESP32** device

### **No Voice Response**

1. **Check AI provider** configuration
2. **Verify microphone** is working
3. **Check audio output** settings
4. **Review server logs** for errors

## 📚 Next Steps

Now that you have the basics working, explore more:

- **[Configuration Guide](../configuration/basic-setup.md)** - Fine-tune your setup
- **[Hardware Guide](../hardware/supported-devices.md)** - Learn about ESP32 devices
- **[Features Guide](../features/voice-interaction.md)** - Explore capabilities
- **[Integrations Guide](../guides/homeassistant.md)** - Connect to other systems

## 🆘 Need Help?

- **Issues?** Check our [Troubleshooting Guide](../support/troubleshooting.md)
- **Questions?** Browse our [FAQ](../support/faq.md)
- **Community?** Join our [GitHub Discussions](https://github.com/lapy/xiaozhi-esp32-server/discussions)

---

## 🎯 Quick Reference

### **Key URLs**
- **Web Interface**: http://localhost:8001
- **OTA Interface**: http://localhost:8003/xiaozhi/ota/
- **API Documentation**: http://localhost:8001/api/docs

### **Key Commands**
```bash
# Start server
docker-compose up -d

# Stop server
docker-compose down

# View logs
docker logs xiaozhi-esp32-server

# Restart server
docker-compose restart
```

### **Configuration Files**
- **Server Config**: `main/xiaozhi-server/config.yaml`
- **Docker Config**: `docker-compose.yml`
- **Environment**: `.env` files

---

**Congratulations! You've successfully set up Xiaozhi ESP32 Server! 🎉**

👉 **[Next: First Device Setup →](first-device.md)**
