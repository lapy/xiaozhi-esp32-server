# ⚙️ Basic Configuration Setup

This guide covers the essential configuration steps to get Xiaozhi ESP32 Server running with your preferred AI providers.

## 🎯 Configuration Overview

Xiaozhi uses a modular configuration system where you can choose different AI providers for each component:

- **ASR (Speech Recognition)**: Convert speech to text
- **LLM (Large Language Model)**: Process and generate responses
- **TTS (Text-to-Speech)**: Convert text to speech
- **VLLM (Vision Language Model)**: Process images and visual content

## 📋 Prerequisites

Before configuring Xiaozhi, ensure you have:

- ✅ **Xiaozhi Server** installed and running
- ✅ **Configuration file** (`data/.config.yaml`) accessible
- ✅ **API keys** for your chosen providers
- ✅ **Model files** downloaded (for local providers)

## 🚀 Quick Configuration

### **Step 1: Access Configuration File**

**For Docker Deployment:**
```bash
# Edit the configuration file
nano xiaozhi-server/data/.config.yaml
```

**For Local Deployment:**
```bash
# Edit the configuration file
nano /path/to/xiaozhi-server/data/.config.yaml
```

### **Step 2: Basic Configuration Template**

```yaml
# Server Configuration
server:
  websocket: ws://YOUR_IP:8000/xiaozhi/v1/
  ota: http://YOUR_IP:8003/xiaozhi/ota/

# AI Module Selection
selected_module:
  VAD: SileroVAD
  ASR: WhisperASR
  LLM: LMStudioLLM
  VLLM: OpenAILLMVLLM
  TTS: EdgeTTS

# AI Provider Configurations
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: null
    output_dir: tmp/

LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    temperature: 0.7
    max_tokens: 1000

TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural
    rate: 1.0
    volume: 1.0
    output_dir: tmp/

# Voice Activity Detection
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700

# Memory Configuration
memory:
  mem_local_short:
    type: local_short
    max_messages: 20
    max_age_hours: 24
```

### **Step 3: Replace Placeholder Values**

1. **Replace `YOUR_IP`** with your actual server IP address
2. **Configure API keys** for cloud providers
3. **Set model paths** for local providers
4. **Adjust parameters** based on your needs

## 🔧 Provider-Specific Configuration

### **Speech Recognition (ASR)**

#### **WhisperASR (Recommended - Offline)**
```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base          # tiny, base, small, medium, large-v1, large-v2, large-v3
    device: auto             # auto, cpu, cuda
    language: null           # null for auto-detect, or specific language code
    output_dir: tmp/
```

#### **OpenAI ASR (Cloud)**
```yaml
ASR:
  OpenAIASR:
    type: openai
    api_key: your_openai_api_key
    model: whisper-1
    language: en
    temperature: 0.0
```

### **Large Language Model (LLM)**

#### **LMStudioLLM (Recommended - Local)**
```yaml
LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
```

#### **OpenAI LLM (Cloud)**
```yaml
LLM:
  OpenAILLM:
    type: openai
    api_key: your_openai_api_key
    model: gpt-4o-mini
    temperature: 0.7
    max_tokens: 1000
```

### **Text-to-Speech (TTS)**

#### **EdgeTTS (Recommended - Free)**
```yaml
TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural    # See available voices below
    rate: 1.0                  # Speech rate (0.5-2.0)
    volume: 1.0                # Volume (0.0-1.0)
    output_dir: tmp/
```

#### **OpenAI TTS (Cloud)**
```yaml
TTS:
  OpenAITTS:
    type: openai
    api_key: your_openai_api_key
    model: tts-1
    voice: alloy              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                # Speech speed (0.25-4.0)
    output_dir: tmp/
```

## 🎤 Voice Configuration

### **Available EdgeTTS Voices**

| Voice | Language | Gender | Description |
|-------|----------|--------|-------------|
| `en-US-AriaNeural` | English (US) | Female | Natural, friendly |
| `en-US-DavisNeural` | English (US) | Male | Professional, clear |
| `en-US-JennyNeural` | English (US) | Female | Warm, conversational |
| `en-US-GuyNeural` | English (US) | Male | Confident, authoritative |
| `en-GB-SoniaNeural` | English (UK) | Female | British accent |
| `en-GB-RyanNeural` | English (UK) | Male | British accent |

### **Voice Activity Detection (VAD)**

```yaml
VAD:
  SileroVAD:
    threshold: 0.5                    # Sensitivity (0.0-1.0)
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700      # Minimum silence before stopping
    pre_padding_ms: 300               # Audio before speech
    post_padding_ms: 300              # Audio after speech
```

## 🧠 Memory Configuration

### **Local Short-term Memory (Recommended)**
```yaml
memory:
  mem_local_short:
    type: local_short
    max_messages: 20          # Maximum messages to remember
    max_age_hours: 24         # Maximum age of memories
    cleanup_interval: 3600    # Cleanup interval in seconds
```

### **Local Long-term Memory**
```yaml
memory:
  mem_local_long:
    type: local_long
    storage_path: data/memory/
    max_entries: 1000
    similarity_threshold: 0.8
```

## 🔄 Testing Configuration

### **Step 1: Restart Services**

```bash
# For Docker deployment
docker restart xiaozhi-esp32-server

# For local deployment
# Restart your Xiaozhi server process
```

### **Step 2: Check Logs**

```bash
# View server logs
docker logs -f xiaozhi-esp32-server

# Look for successful initialization messages
```

### **Step 3: Test Voice Interaction**

1. **Wake up your ESP32 device**
2. **Speak a test phrase**
3. **Check server logs** for processing steps
4. **Verify response** is generated correctly

## 🛠️ Common Configuration Issues

### **Issue: "Model not found" Error**
**Solution:** Ensure model files are downloaded and paths are correct
```bash
# Check if model directory exists
ls -la models/
```

### **Issue: "API key invalid" Error**
**Solution:** Verify API keys are correct and have proper permissions
```yaml
# Double-check API key format
api_key: sk-your-actual-api-key-here
```

### **Issue: "Connection timeout" Error**
**Solution:** Check network connectivity and service availability
```bash
# Test API endpoint
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

### **Issue: "Audio file not found" Error**
**Solution:** Ensure output directories exist and are writable
```bash
# Create output directories
mkdir -p tmp/
chmod 755 tmp/
```

## 🎯 Next Steps

After basic configuration:

1. **[Advanced Configuration](advanced.md)** - Fine-tune settings
2. **[Provider Configuration](providers.md)** - Detailed provider setup
3. **[Configuration Examples](examples.md)** - Real-world examples
4. **[Testing Your Setup](../getting-started/first-device.md)** - Verify everything works

## 🆘 Need Help?

- **Configuration Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Provider Questions?** See [Provider Configuration](providers.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Essential Configuration**
```yaml
selected_module:
  ASR: WhisperASR      # Offline speech recognition
  LLM: LMStudioLLM     # Local language model
  TTS: EdgeTTS         # Free text-to-speech
```

### **Key Directories**
- **Models**: `models/` - AI model files
- **Data**: `data/` - Configuration and data
- **Temp**: `tmp/` - Temporary audio files

### **Important URLs**
- **WebSocket**: `ws://YOUR_IP:8000/xiaozhi/v1/`
- **OTA Interface**: `http://YOUR_IP:8003/xiaozhi/ota/`

---

**Your basic configuration is ready! 🎉**

👉 **[Next: Advanced Configuration →](advanced.md)**
