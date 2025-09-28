# 🔌 Device Flashing Guide

This guide covers how to flash firmware to your ESP32 device using various methods.

## 🎯 Flashing Methods Overview

Choose the method that works best for your setup:

- **Web-based Flashing** (Recommended) - No software installation required
- **Command Line Flashing** - For developers and advanced users
- **IDE Flashing** - Using Arduino IDE or PlatformIO
- **OTA Flashing** - Over-the-air updates for existing devices

## 🌐 Web-based Flashing (Recommended)

### **Step 1: Prepare Your Device**

1. **Connect ESP32** to your computer via USB
2. **Install USB drivers** if needed (usually automatic on Windows/Mac)
3. **Identify COM port** (Windows) or device path (Mac/Linux)

**Windows:**
- Open Device Manager → Ports (COM & LPT)
- Look for "Silicon Labs CP210x" or similar

**Mac/Linux:**
```bash
# List USB devices
ls /dev/tty.*
# Look for /dev/tty.usbserial-* or /dev/ttyUSB*
```

### **Step 2: Access ESP-Launchpad**

1. **Open Chrome browser** (recommended for best compatibility)
2. **Navigate to**: https://espressif.github.io/esp-launchpad/
3. **Allow camera/microphone** permissions if prompted

### **Step 3: Upload Firmware**

1. **Click "Choose File"** or drag and drop your firmware file
2. **Select your firmware**: `merged-binary.bin` (from firmware compilation)
3. **Click "Connect"** and select your ESP32 device
4. **Wait for connection** to be established

### **Step 4: Flash Firmware**

1. **Click "Flash"** to start the flashing process
2. **Wait for completion** (usually 30-60 seconds)
3. **Device will restart** automatically after flashing
4. **Check console output** for any errors

### **Step 5: Verify Installation**

1. **Check device status** - LED indicators should show normal operation
2. **Test wake word** - Say "Hey Xiaozhi" or configured wake word
3. **Check server logs** - Look for device connection in server logs

## 💻 Command Line Flashing

### **Prerequisites**

- **ESP-IDF** development environment installed
- **esptool.py** available in your PATH
- **Firmware file** ready for flashing

### **Step 1: Install esptool**

```bash
# Install esptool if not already installed
pip install esptool

# Verify installation
esptool.py version
```

### **Step 2: Identify Device**

```bash
# List available serial ports
esptool.py --port auto chip_id

# Or specify port directly
esptool.py --port COM3 chip_id  # Windows
esptool.py --port /dev/ttyUSB0 chip_id  # Linux
esptool.py --port /dev/tty.usbserial-* chip_id  # Mac
```

### **Step 3: Flash Firmware**

```bash
# Basic flashing command
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 merged-binary.bin

# With verification
esptool.py --chip esp32s3 --port COM3 --baud 921600 --verify write_flash 0x0 merged-binary.bin

# With progress indicator
esptool.py --chip esp32s3 --port COM3 --baud 921600 --verify --progress write_flash 0x0 merged-binary.bin
```

### **Step 4: Advanced Flashing Options**

```bash
# Flash with specific memory layout
esptool.py --chip esp32s3 --port COM3 --baud 921600 \
  --flash_mode dio \
  --flash_freq 80m \
  --flash_size 16MB \
  write_flash 0x0 merged-binary.bin

# Flash multiple files
esptool.py --chip esp32s3 --port COM3 --baud 921600 \
  write_flash 0x0 bootloader.bin \
  0x8000 partition-table.bin \
  0x10000 merged-binary.bin
```

## 🔧 IDE Flashing

### **Arduino IDE Method**

#### **Step 1: Install ESP32 Board Package**

1. **Open Arduino IDE**
2. **Go to**: File → Preferences
3. **Add board manager URL**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. **Go to**: Tools → Board → Boards Manager
5. **Search for "ESP32"** and install "ESP32 by Espressif Systems"

#### **Step 2: Configure Board**

1. **Select board**: Tools → Board → ESP32 Arduino → ESP32S3 Dev Module
2. **Select port**: Tools → Port → [Your COM port]
3. **Configure settings**:
   - **Upload Speed**: 921600
   - **Flash Mode**: DIO
   - **Flash Frequency**: 80MHz
   - **Flash Size**: 16MB

#### **Step 3: Flash Firmware**

1. **Open firmware file** (if available as .ino)
2. **Click Upload** button
3. **Wait for completion**

### **PlatformIO Method**

#### **Step 1: Install PlatformIO**

```bash
# Install PlatformIO
pip install platformio

# Or use PlatformIO IDE
# Download from: https://platformio.org/install/ide
```

#### **Step 2: Create Project**

```bash
# Create new project
pio project init --board esp32s3-devkitc-1

# Or use existing project
cd your-project-directory
```

#### **Step 3: Configure platformio.ini**

```ini
[env:esp32s3]
platform = espressif32
board = esp32s3-devkitc-1
framework = arduino
monitor_speed = 115200
upload_speed = 921600
```

#### **Step 4: Flash Firmware**

```bash
# Upload firmware
pio run --target upload

# Monitor serial output
pio device monitor
```

## 📡 OTA (Over-the-Air) Flashing

### **Prerequisites**

- **Device already running** Xiaozhi firmware
- **Network connectivity** to your server
- **OTA interface** accessible
- **New firmware file** ready

### **Step 1: Prepare OTA Update**

1. **Access OTA interface**: `http://YOUR_IP:8003/xiaozhi/ota/`
2. **Verify interface** shows "OTA interface is running normally"
3. **Prepare firmware file** for upload

### **Step 2: Upload Firmware**

1. **Click "Choose File"** in OTA interface
2. **Select new firmware** file
3. **Click "Upload"** to start OTA update
4. **Wait for upload** to complete

### **Step 3: Trigger Update**

1. **Wake up device** using wake word
2. **Say "Update firmware"** or similar command
3. **Device will download** and install new firmware
4. **Device will restart** automatically

### **Step 4: Verify Update**

1. **Check device status** after restart
2. **Test functionality** with voice commands
3. **Check server logs** for successful connection

## 🛠️ Troubleshooting Flashing Issues

### **Common Issues and Solutions**

#### **"Port not found" Error**
```bash
# Check available ports
esptool.py --port auto chip_id

# Install USB drivers
# Windows: Download from Silicon Labs website
# Mac: Usually automatic
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
```

#### **"Failed to connect" Error**
1. **Hold BOOT button** while pressing RESET
2. **Release RESET** while holding BOOT
3. **Release BOOT** after 2 seconds
4. **Try flashing again**

#### **"Flash write error" Error**
```bash
# Try slower baud rate
esptool.py --chip esp32s3 --port COM3 --baud 115200 write_flash 0x0 merged-binary.bin

# Try different flash mode
esptool.py --chip esp32s3 --port COM3 --baud 921600 --flash_mode qio write_flash 0x0 merged-binary.bin
```

#### **"Verification failed" Error**
```bash
# Flash without verification first
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 merged-binary.bin

# Then verify separately
esptool.py --chip esp32s3 --port COM3 --baud 921600 verify_flash 0x0 merged-binary.bin
```

#### **"Device not responding" Error**
1. **Check USB cable** - use data cable, not charging cable
2. **Try different USB port** - prefer USB 2.0 ports
3. **Check power supply** - ensure stable 5V supply
4. **Reset device** - press RESET button

### **Advanced Troubleshooting**

#### **Erase Flash Before Flashing**
```bash
# Erase entire flash
esptool.py --chip esp32s3 --port COM3 erase_flash

# Erase specific sectors
esptool.py --chip esp32s3 --port COM3 erase_region 0x0 0x400000
```

#### **Read Flash for Verification**
```bash
# Read flash content
esptool.py --chip esp32s3 --port COM3 read_flash 0x0 0x400000 flash_content.bin

# Compare with original
diff merged-binary.bin flash_content.bin
```

#### **Reset to Factory Settings**
```bash
# Erase flash and reset
esptool.py --chip esp32s3 --port COM3 erase_flash
esptool.py --chip esp32s3 --port COM3 run
```

## 🔍 Flashing Verification

### **Step 1: Check Flash Content**

```bash
# Read flash and verify
esptool.py --chip esp32s3 --port COM3 verify_flash 0x0 merged-binary.bin
```

### **Step 2: Monitor Boot Process**

```bash
# Monitor serial output during boot
esptool.py --chip esp32s3 --port COM3 monitor
```

### **Step 3: Test Device Functionality**

1. **Power on device**
2. **Check LED indicators**
3. **Test wake word detection**
4. **Verify server connection**

## 📊 Flashing Performance Tips

### **Optimize Flashing Speed**

```bash
# Use maximum baud rate
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 merged-binary.bin

# Use optimal flash mode
esptool.py --chip esp32s3 --port COM3 --baud 921600 --flash_mode dio write_flash 0x0 merged-binary.bin
```

### **Batch Flashing Multiple Devices**

```bash
#!/bin/bash
# Flash multiple devices script

DEVICES=("/dev/ttyUSB0" "/dev/ttyUSB1" "/dev/ttyUSB2")
FIRMWARE="merged-binary.bin"

for device in "${DEVICES[@]}"; do
    echo "Flashing $device..."
    esptool.py --chip esp32s3 --port "$device" --baud 921600 write_flash 0x0 "$FIRMWARE"
    if [ $? -eq 0 ]; then
        echo "Successfully flashed $device"
    else
        echo "Failed to flash $device"
    fi
done
```

## 🎯 Next Steps

After successful flashing:

1. **[Configure Your Device](../getting-started/first-device.md)** - Complete device setup
2. **[Test Voice Interaction](../features/voice-interaction.md)** - Verify functionality
3. **[Configure AI Providers](../configuration/providers.md)** - Set up AI services
4. **[Hardware Troubleshooting](troubleshooting.md)** - Common hardware issues

## 🆘 Need Help?

- **Flashing Issues?** Check [Troubleshooting](troubleshooting.md)
- **Hardware Questions?** See [Supported Devices](supported-devices.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Flashing Commands**
```bash
# Web-based (recommended)
https://espressif.github.io/esp-launchpad/

# Command line
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 merged-binary.bin

# OTA update
http://YOUR_IP:8003/xiaozhi/ota/
```

### **Common Ports**
- **Windows**: COM3, COM4, COM5...
- **Mac**: /dev/tty.usbserial-*
- **Linux**: /dev/ttyUSB0, /dev/ttyUSB1...

### **Troubleshooting Steps**
1. Check USB connection
2. Install drivers
3. Try different baud rate
4. Hold BOOT button during reset
5. Use web-based flashing

---

**Your device is ready to flash! 🎉**

👉 **[Next: Hardware Troubleshooting →](troubleshooting.md)**
