# 🔧 Hardware Troubleshooting

This guide helps you diagnose and fix common hardware issues with ESP32 devices and Xiaozhi ESP32 Server.

## 🎯 Troubleshooting Overview

This guide covers:
- **Device connection** issues
- **Audio problems** (microphone/speaker)
- **Power and stability** issues
- **Network connectivity** problems
- **Performance optimization** tips

## 🔌 Device Connection Issues

### **Device Not Detected**

#### **Symptoms**
- Device not showing up in Device Manager
- "Port not found" errors
- No response from flashing tools

#### **Solutions**

**1. Check USB Connection**
```bash
# Windows: Check Device Manager
# Look for "Silicon Labs CP210x" or similar

# Mac: Check system information
system_profiler SPUSBDataType

# Linux: Check USB devices
lsusb
```

**2. Install USB Drivers**
- **Windows**: Download CP210x drivers from Silicon Labs
- **Mac**: Usually automatic, may need Xcode Command Line Tools
- **Linux**: Add user to dialout group
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**3. Try Different USB Ports**
- Use **USB 2.0 ports** (more stable than USB 3.0)
- Avoid **USB hubs** (use direct connection)
- Try **different cables** (ensure data cable, not charging cable)

**4. Reset Device**
```bash
# Hold BOOT button, press RESET, release RESET, release BOOT
# This puts device in download mode
```

### **Flashing Failures**

#### **Symptoms**
- "Failed to connect" errors
- "Flash write error" messages
- Verification failures

#### **Solutions**

**1. Use Correct Baud Rate**
```bash
# Try different baud rates
esptool.py --chip esp32s3 --port COM3 --baud 115200 write_flash 0x0 firmware.bin
esptool.py --chip esp32s3 --port COM3 --baud 460800 write_flash 0x0 firmware.bin
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 firmware.bin
```

**2. Try Different Flash Modes**
```bash
# Try different flash modes
esptool.py --chip esp32s3 --port COM3 --flash_mode dio write_flash 0x0 firmware.bin
esptool.py --chip esp32s3 --port COM3 --flash_mode qio write_flash 0x0 firmware.bin
```

**3. Erase Flash First**
```bash
# Erase entire flash
esptool.py --chip esp32s3 --port COM3 erase_flash

# Then flash normally
esptool.py --chip esp32s3 --port COM3 write_flash 0x0 firmware.bin
```

**4. Use Web-based Flashing**
- Navigate to: https://espressif.github.io/esp-launchpad/
- Often more reliable than command line tools

## 🎤 Audio Issues

### **No Audio Input (Microphone)**

#### **Symptoms**
- Device not responding to wake word
- No audio detected in server logs
- "No audio input" errors

#### **Solutions**

**1. Check Microphone Connections**
```
ESP32-S3 Pinout:
- GPIO 15: Microphone WS (Word Select)
- GPIO 16: Microphone BCK (Bit Clock)
- GPIO 17: Microphone DIN (Data Input)
- 3.3V: Power supply
- GND: Ground
```

**2. Verify Microphone Type**
- **I2S Microphones**: SPH0645LM4H, INMP441, ICS-43434
- **Analog Microphones**: MAX9814, MAX4466, ADMP401
- **Check datasheet** for correct pin connections

**3. Test Microphone Functionality**
```bash
# Check if microphone is detected
# Look for I2S initialization in device logs
```

**4. Adjust Audio Settings**
```yaml
# In configuration file
audio:
  sample_rate: 16000
  channels: 1
  bit_depth: 16
  buffer_size: 4096
  gain: 1.0  # Adjust if audio is too quiet/loud
```

### **No Audio Output (Speaker)**

#### **Symptoms**
- No sound from device
- TTS responses not audible
- "Audio output failed" errors

#### **Solutions**

**1. Check Speaker Connections**
```
ESP32-S3 Pinout:
- GPIO 18: Speaker DOUT (Data Output)
- GPIO 19: Speaker BCK (Bit Clock)
- GPIO 20: Speaker LRC (Left/Right Clock)
- 3.3V: Power supply
- GND: Ground
```

**2. Verify Speaker Type**
- **I2S Speakers**: MAX98357A, PCM5102A
- **Analog Speakers**: Use amplifier (PAM8403, TDA2822)
- **Check power requirements** (3.3V, 5V, or external power)

**3. Test Speaker Functionality**
```bash
# Check if speaker is detected
# Look for I2S output initialization in device logs
```

**4. Adjust Audio Settings**
```yaml
# In configuration file
TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural
    rate: 1.0
    volume: 1.0  # Adjust volume level
    output_dir: tmp/
```

### **Poor Audio Quality**

#### **Symptoms**
- Distorted audio
- Low volume
- Background noise
- Echo or feedback

#### **Solutions**

**1. Improve Audio Quality**
```yaml
# Optimize audio settings
audio:
  sample_rate: 44100  # Higher sample rate for better quality
  bit_depth: 24       # Higher bit depth
  buffer_size: 8192   # Larger buffer for stability
  gain: 0.8          # Reduce gain to prevent distortion
```

**2. Reduce Background Noise**
- **Position microphone** away from speaker
- **Use directional microphone** (cardioid pattern)
- **Add acoustic foam** around device
- **Reduce ambient noise** in environment

**3. Fix Echo/Feedback**
- **Increase distance** between microphone and speaker
- **Use echo cancellation** in audio processing
- **Adjust VAD settings** to prevent feedback loops

## ⚡ Power and Stability Issues

### **Device Crashes or Reboots**

#### **Symptoms**
- Device randomly restarts
- "Brownout" errors in logs
- Unstable operation

#### **Solutions**

**1. Check Power Supply**
- **Use stable 5V supply** (not USB power from computer)
- **Check current capacity** (ESP32-S3 needs ~500mA)
- **Use quality USB cable** with proper gauge wires
- **Add capacitors** for power smoothing

**2. Monitor Power Consumption**
```bash
# Check power consumption
# ESP32-S3: ~240mA active, ~10mA sleep
# Add components: microphone (~1mA), speaker (~100mA)
```

**3. Optimize Power Settings**
```yaml
# In configuration file
power:
  cpu_freq: 240  # MHz (80, 160, 240)
  sleep_mode: light_sleep  # light_sleep, deep_sleep
  wifi_power_save: true
```

### **WiFi Connection Issues**

#### **Symptoms**
- Device can't connect to WiFi
- Frequent disconnections
- "WiFi connection failed" errors

#### **Solutions**

**1. Check WiFi Settings**
```yaml
# In configuration file
wifi:
  ssid: "YourWiFiNetwork"
  password: "YourWiFiPassword"
  # Use 2.4GHz band (ESP32 doesn't support 5GHz)
```

**2. Improve Signal Strength**
- **Position device** closer to router
- **Use WiFi extender** if needed
- **Check for interference** (microwaves, Bluetooth devices)
- **Use 2.4GHz band** (ESP32 doesn't support 5GHz)

**3. Debug WiFi Connection**
```bash
# Check WiFi status in device logs
# Look for connection attempts and failures
```

## 🌐 Network Connectivity Issues

### **Can't Connect to Server**

#### **Symptoms**
- Device connects to WiFi but not to server
- "Server connection failed" errors
- No communication with Xiaozhi server

#### **Solutions**

**1. Check Server Configuration**
```yaml
# In configuration file
server:
  websocket: ws://YOUR_IP:8000/xiaozhi/v1/
  ota: http://YOUR_IP:8003/xiaozhi/ota/
```

**2. Verify Network Connectivity**
```bash
# Test from device (if possible)
ping YOUR_SERVER_IP

# Test from server
ping DEVICE_IP
```

**3. Check Firewall Settings**
- **Allow ports** 8000 (WebSocket) and 8003 (OTA)
- **Check NAT settings** if using router
- **Verify IP addresses** are correct

**4. Test OTA Interface**
- **Open OTA URL**: `http://YOUR_IP:8003/xiaozhi/ota/`
- **Should show**: "OTA interface is running normally"
- **If not working**: Check server configuration

### **4G Mode Connection Issues**

#### **Symptoms**
- Works on WiFi but not on 4G
- "Secure connection required" errors
- Can't connect via mobile data

#### **Solutions**

**1. Enable HTTPS/WSS**
```yaml
# In configuration file
server:
  websocket: wss://YOUR_DOMAIN:8000/xiaozhi/v1/  # Note: wss://
  ota: https://YOUR_DOMAIN:8003/xiaozhi/ota/     # Note: https://
```

**2. Configure SSL Certificates**
```yaml
# SSL configuration
ssl:
  enabled: true
  cert_file: /path/to/cert.pem
  key_file: /path/to/key.pem
```

**3. Use Domain Name**
- **ESP32 firmware** requires secure connections for 4G
- **Use domain name** instead of IP address
- **Configure DNS** properly

## 🚀 Performance Optimization

### **Slow Response Times**

#### **Symptoms**
- Long delays between speech and response
- "Processing timeout" errors
- Poor user experience

#### **Solutions**

**1. Optimize AI Models**
```yaml
# Use faster models
ASR:
  WhisperASR:
    model_name: tiny  # Instead of base/small/medium/large
    device: cuda      # Use GPU if available

LLM:
  LMStudioLLM:
    model_name: llama-3.1:8b  # Smaller model
    context_length: 2048      # Smaller context window
```

**2. Enable Streaming**
```yaml
# Enable streaming for faster responses
streaming:
  enabled: true
  buffer_size: 1024
  chunk_size: 512
```

**3. Optimize Network**
- **Use local AI providers** (LMStudio, WhisperASR)
- **Reduce network latency** (local server)
- **Optimize WiFi connection** (strong signal)

### **High Memory Usage**

#### **Symptoms**
- Device running out of memory
- "Memory allocation failed" errors
- Crashes due to memory issues

#### **Solutions**

**1. Reduce Memory Usage**
```yaml
# Optimize memory settings
memory:
  mem_local_short:
    max_messages: 10      # Reduce from default 20
    max_age_hours: 12    # Reduce from default 24

# Reduce audio buffer sizes
audio:
  buffer_size: 2048      # Reduce from default 4096
  chunk_size: 512        # Reduce from default 1024
```

**2. Use Smaller Models**
```yaml
# Use smaller AI models
ASR:
  WhisperASR:
    model_name: tiny      # 39MB instead of 142MB (base)

LLM:
  LMStudioLLM:
    model_name: llama-3.1:8b  # Smaller context window
    context_length: 1024      # Reduce from default 4096
```

## 🔍 Diagnostic Tools

### **Device Status Check**

```bash
# Check device information
esptool.py --chip esp32s3 --port COM3 chip_id
esptool.py --chip esp32s3 --port COM3 flash_id

# Monitor serial output
esptool.py --chip esp32s3 --port COM3 monitor
```

### **Network Diagnostics**

```bash
# Test network connectivity
ping YOUR_SERVER_IP
telnet YOUR_SERVER_IP 8000
curl http://YOUR_SERVER_IP:8003/xiaozhi/ota/
```

### **Audio Testing**

```bash
# Test microphone (if supported)
# Look for I2S initialization messages in logs

# Test speaker (if supported)
# Look for audio output messages in logs
```

## 📊 Performance Monitoring

### **Monitor Device Performance**

```yaml
# Enable performance monitoring
monitoring:
  enabled: true
  
  metrics:
    response_time: true
    memory_usage: true
    cpu_usage: true
    audio_processing_time: true
  
  # Log performance data
  logging:
    level: INFO
    performance_logs: true
```

### **Common Performance Metrics**

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| **Response Time** | < 2s | 2-5s | > 5s |
| **Memory Usage** | < 70% | 70-90% | > 90% |
| **CPU Usage** | < 80% | 80-95% | > 95% |
| **Audio Latency** | < 100ms | 100-300ms | > 300ms |

## 🛠️ Advanced Troubleshooting

### **Firmware Issues**

#### **Corrupted Firmware**
```bash
# Erase and reflash
esptool.py --chip esp32s3 --port COM3 erase_flash
esptool.py --chip esp32s3 --port COM3 write_flash 0x0 firmware.bin
```

#### **Boot Loop Issues**
```bash
# Check boot logs
esptool.py --chip esp32s3 --port COM3 monitor

# Look for boot errors and stack traces
```

### **Hardware Debugging**

#### **Use Oscilloscope**
- **Check clock signals** (I2S BCK, WS)
- **Verify data signals** (I2S DIN, DOUT)
- **Monitor power supply** stability

#### **Use Logic Analyzer**
- **Capture I2S communication**
- **Verify protocol compliance**
- **Check timing requirements**

## 🎯 Next Steps

After resolving hardware issues:

1. **[Test Voice Interaction](../features/voice-interaction.md)** - Verify functionality
2. **[Configure AI Providers](../configuration/providers.md)** - Set up AI services
3. **[Performance Optimization](../guides/performance.md)** - Optimize for your use case
4. **[Advanced Configuration](../configuration/advanced.md)** - Fine-tune settings

## 🆘 Need Help?

- **Hardware Issues?** Check [Supported Devices](supported-devices.md)
- **Flashing Problems?** See [Device Flashing](flashing.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Common Issues**
- **Device not detected**: Check USB drivers and connections
- **No audio**: Verify microphone/speaker connections
- **WiFi issues**: Check 2.4GHz network and signal strength
- **Performance**: Use smaller models and enable streaming

### **Diagnostic Commands**
```bash
# Check device
esptool.py --chip esp32s3 --port COM3 chip_id

# Monitor logs
esptool.py --chip esp32s3 --port COM3 monitor

# Test network
ping YOUR_SERVER_IP
curl http://YOUR_SERVER_IP:8003/xiaozhi/ota/
```

### **Emergency Recovery**
```bash
# Erase and reflash
esptool.py --chip esp32s3 --port COM3 erase_flash
esptool.py --chip esp32s3 --port COM3 write_flash 0x0 firmware.bin
```

---

**Your hardware troubleshooting guide is ready! 🎉**

👉 **[Next: Test Voice Interaction →](../features/voice-interaction.md)**
