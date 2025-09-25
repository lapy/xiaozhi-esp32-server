# 📋 Prerequisites

Before you start building with Xiaozhi ESP32 Server, let's make sure you have everything you need for a smooth setup experience.

## 🖥️ System Requirements

### **Operating System**
- **Windows 10/11** (64-bit)
- **macOS 10.15+** (Intel or Apple Silicon)
- **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+)

### **Hardware Requirements**
- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for AI services

### **Development Environment**
- **Python 3.10+** (for local installation)
- **Node.js 16+** (for web interface)
- **Git** (for cloning repositories)

## 🔧 Required Software

### **Essential Tools**

#### **Docker** (Recommended)
```bash
# Windows/macOS: Download from https://docker.com
# Linux: Install via package manager
sudo apt update
sudo apt install docker.io docker-compose
```

#### **Python Environment** (Alternative)
```bash
# Install Python 3.10+
# Windows: Download from python.org
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10 python3.10-venv
```

#### **Git**
```bash
# Windows: Download from git-scm.com
# macOS: brew install git
# Linux: sudo apt install git
```

### **Optional but Recommended**

#### **Visual Studio Code**
- **Extensions**: Python, Docker, GitLens
- **Download**: [code.visualstudio.com](https://code.visualstudio.com)

#### **Postman** (API Testing)
- **Download**: [postman.com](https://postman.com)

## 🔌 Hardware Requirements

### **ESP32 Development Board**
Choose one of these popular options:

#### **🏆 Recommended Boards**
- **ESP32-S3-DevKitC-1** - Official Espressif board
- **ESP32-S3-BOX** - With built-in microphone and speaker
- **ESP32-S3-BOX-3** - Latest version with improved audio
- **ESP32-S3-Korvo-2** - Audio-focused development board

#### **💡 Budget Options**
- **ESP32-DevKitC** - Basic development board
- **ESP32-WROOM-32** - Module with development board
- **ESP32-S2-Saola-1** - Single-core option

#### **🎯 Specialized Boards**
- **ESP32-S3-BOX-Lite** - Compact version
- **ESP32-S3-USB-OTG** - USB OTG support
- **ESP32-S3-EYE** - With camera and microphone

### **Audio Components** (if not included)

#### **Microphone**
- **SPH0645LM4H** - Digital MEMS microphone
- **INMP441** - I2S digital microphone
- **MAX9814** - Analog microphone with AGC

#### **Speaker**
- **Small speaker** (8Ω, 0.5W+)
- **Amplifier module** (PAM8403, MAX98357A)
- **Audio jack** for external speakers

### **Additional Components**
- **USB Cable** (Type-C or Micro-USB)
- **Breadboard** and jumper wires
- **Resistors** (10kΩ, 4.7kΩ)
- **Capacitors** (100µF, 10µF)

## 🌐 Internet Requirements

### **AI Service Access**
You'll need access to at least one AI service:

#### **Free Options**
- **OpenAI API** - GPT models (requires API key)
- **Whisper** - Local speech recognition (free)
- **EdgeTTS** - Microsoft text-to-speech (free)
- **LMStudio** - Local LLM hosting (free)

#### **Paid Options**
- **OpenAI GPT-4** - Advanced language models
- **Google Gemini** - Alternative LLM provider
- **Azure Cognitive Services** - Microsoft AI services

### **Network Configuration**
- **Port 8000** - WebSocket communication
- **Port 8001** - Web management interface
- **Port 8003** - OTA updates
- **HTTPS** - For secure connections (optional)

## 🎯 AI Provider Setup

### **Choose Your AI Stack**

#### **🆓 Free Tier Setup**
```yaml
ASR: WhisperASR          # Local speech recognition
LLM: LMStudioLLM         # Local language model
TTS: EdgeTTS             # Free text-to-speech
```

#### **💎 Premium Setup**
```yaml
ASR: OpenAIASR           # OpenAI Whisper API
LLM: OpenAILLM           # GPT-4 or GPT-3.5
TTS: OpenAITTS           # OpenAI TTS
```

#### **🔒 Privacy-Focused Setup**
```yaml
ASR: WhisperASR          # Local processing
LLM: LMStudioLLM         # Local processing
TTS: EdgeTTS             # Local processing
```

### **API Keys Required**

#### **OpenAI** (Optional)
- **Sign up**: [platform.openai.com](https://platform.openai.com)
- **Get API key**: Account → API Keys
- **Add billing**: Required for API usage

#### **Google** (Optional)
- **Sign up**: [console.cloud.google.com](https://console.cloud.google.com)
- **Enable APIs**: Speech-to-Text, Text-to-Speech
- **Create credentials**: Service account key

## 🛠️ Development Tools

### **ESP32 Development**

#### **ESP-IDF** (Espressif IoT Development Framework)
```bash
# Install ESP-IDF
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
```

#### **Arduino IDE** (Alternative)
- **Download**: [arduino.cc](https://arduino.cc)
- **Install ESP32 board package**
- **Install required libraries**

### **Firmware Flashing Tools**

#### **esptool.py**
```bash
pip install esptool
```

#### **ESP32 Flash Tool**
- **Windows**: [ESP32 Flash Download Tool](https://espressif.com)
- **Web-based**: [ESP-Launchpad](https://espressif.github.io/esp-launchpad/)

## 📱 Mobile App (Optional)

### **Manager Mobile App**
- **Platform**: UniApp-based mobile app
- **Features**: Device management, configuration
- **Installation**: Via package managers or direct download

## ✅ Pre-Flight Checklist

Before you start, verify you have:

- [ ] **Compatible operating system**
- [ ] **Docker installed** (or Python 3.10+)
- [ ] **ESP32 development board**
- [ ] **USB cable** for ESP32
- [ ] **Internet connection**
- [ ] **AI service API key** (if using cloud services)
- [ ] **Basic electronics knowledge** (helpful but not required)

## 🚀 Ready to Start?

Once you have everything on the checklist, you're ready to begin!

👉 **[Next: Quick Start →](quick-start.md)**

## 🆘 Need Help?

- **Missing something?** Check our [Troubleshooting Guide](../support/troubleshooting.md)
- **Hardware questions?** See [Supported Devices](../hardware/supported-devices.md)
- **AI provider setup?** Check [Configuration Guide](../configuration/providers.md)

---

*Let's build something amazing! 🚀*
