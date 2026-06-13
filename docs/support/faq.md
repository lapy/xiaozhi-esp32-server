# ❓ Frequently Asked Questions

Get answers to the most common questions about Xiaozhi ESP32 Server based on real user experiences and issues.

## 🚀 Getting Started

### **Q: Why does Xiaozhi recognize multiple languages when I speak? 🌍**

**Suggestion:** Check if the `models` directory has model files. If not, download them from the [Deployment Guide](../installation/docker.md#model-files).

This usually happens when:
- No ASR model files are present
- Using a multilingual model without language specification
- Model files are corrupted or incomplete

**Solution:**
1. Download the appropriate Vosk English model
2. Ensure model files are in the correct directory structure
3. Verify model configuration in `.config.yaml`

### **Q: Why does the error "TTS task failed: file not found" occur? 📁**

**Suggestion:** Check if you have installed `libopus` and `ffmpeg` using `conda`. If not, install them.

**Common causes:**
- Missing audio codec libraries
- Incorrect file paths in configuration
- Permission issues with temporary files

**Solution:**
```bash
# Install required dependencies
conda install libopus -y
conda install ffmpeg -y

# Or using pip
pip install ffmpeg-python
```

### **Q: Why does TTS often fail and timeout? ⏰**

**Suggestion:** If TTS often fails, please check if you are using a proxy. If so, try disabling the proxy and retrying.

**Common causes:**
- Network proxy interference
- Slow internet connection
- TTS service rate limits
- Firewall blocking requests

**Solutions:**
1. **Disable proxy** for TTS services
2. **Use local TTS** (EdgeTTS) instead of cloud services
3. **Check network connectivity** to TTS providers
4. **Increase timeout values** in configuration

### **Q: Why can't I connect to the self-built server using 4G mode? 🔐**

**Reason:** The firmware of the ESP32 board requires a secure connection in 4G mode.

**Solution:** There are two ways to solve this problem:

1. **Modify the code** to use a secure connection
2. **Use nginx** to configure an SSL certificate

For detailed instructions, refer to the project documentation or GitHub issues.

### **Q: How can I improve Xiaozhi's conversation response speed? ⚡**

**Suggestion:** The default configuration of this project is a low-cost solution. We recommend that beginners use the default free model to solve the "running" problem first, and then optimize the "running fast" problem.

**Performance Optimization Table:**

| Module Name | Default Free Configuration | Streaming Configuration |
|:---:|:---:|:---:|
| ASR (Speech Recognition) | OpenaiASR (API) or **WhisperASR (Local)** | 👍OpenaiASR (API) or 👍GroqASR (API) or **👍WhisperASR (Local)** |
| LLM (Large Model) | OpenAILLM (OpenAI gpt-4o-mini) | 👍LMStudioLLM (Local llama3.1:8b) |
| VLLM (Visual Large Model) | OpenAILLMVLLM (OpenAI gpt-4o) | 👍OpenAILLMVLLM (OpenAI gpt-4o) |
| TTS (Text-to-Speech) | ✅EdgeTTS (Microsoft Edge TTS) | 👍OpenAITTS (OpenAI TTS) |
| Intent (Intent Recognition) | function_call (Function Call) | function_call (Function Call) |
| Memory (Memory Function) | mem_local_short (Local Short-term Memory) | mem_local_short (Local Short-term Memory) |

**Streaming Configuration Benefits:**
- Improves response speed by about **2.5 seconds** compared to early versions
- Enables real-time processing
- Reduces overall latency

### **Q: Why does Xiaozhi often interrupt when I speak slowly with pauses? 🗣️**

**Suggestion:** In the configuration file, find the following part and increase the value of `min_silence_duration_ms` (e.g., to `1000`):

```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700  # If you speak slowly, you can increase this value
```

**Configuration Options:**
- **Increase `min_silence_duration_ms`** to 1000-1500ms for slow speakers
- **Adjust `threshold`** to be less sensitive (0.3-0.4)
- **Enable `pre_padding_ms`** and `post_padding_ms` for better detection

## 🔧 Technical Issues

### **Q: Can I connect to self-built server using WiFi, but 4G mode cannot connect?**

**Reason:** 4G mode requires secure connections (HTTPS/WSS) while WiFi allows HTTP/WS.

**Solutions:**
1. **Configure SSL certificates** for your server
2. **Use nginx reverse proxy** with SSL termination
3. **Modify ESP32 firmware** to support secure connections
4. **Use domain name** instead of IP address

### **Q: I want to control lights, air conditioning, remote power on/off through Xiaozhi**

**Solution:** Integrate with HomeAssistant using the built-in function calling capabilities.

**Steps:**
1. **Set up HomeAssistant** with your smart devices
2. **Configure Xiaozhi** to use function calling
3. **Add HomeAssistant integration** in agent configuration
4. **Test voice commands** like "Turn on the living room light"

See the [HomeAssistant Integration Guide](../guides/homeassistant.md) for detailed instructions.

## 🎤 Speech Recognition Issues

### **Q: How to use Whisper ASR for offline speech recognition? 🎤**

**Whisper ASR** is a powerful offline speech recognition solution that provides excellent accuracy for multilingual speech recognition.

**Configuration:**
```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base  # Choose from: tiny, base, small, medium, large-v1, large-v2, large-v3
    device: auto      # auto, cpu, cuda
    language: null    # null for auto-detect, or specific language code
    output_dir: tmp/
```

**Key Features:**
- **Offline Operation**: Complete offline after initial model download
- **Multilingual Support**: Supports 99+ languages with auto-detection
- **Multiple Model Sizes**: From tiny (39MB) to large-v3 (1.5GB)
- **GPU Acceleration**: Automatic CUDA detection and usage
- **High Accuracy**: State-of-the-art accuracy for speech recognition

**Model Selection Guide:**
- **tiny/base**: Fast processing, good for real-time applications
- **small/medium**: Better accuracy, slower processing
- **large-v1/v2/v3**: Highest accuracy, slowest processing

For detailed setup instructions, see: [Whisper ASR Integration Guide](../guides/whisper-asr.md)

## 🔧 Deployment Issues

### **Q: Which deployment method should I choose?**

**Method 1: Simple Server Deployment**
- **Best for**: Beginners, testing, basic voice interaction
- **Components**: Server only
- **Configuration**: Minimal setup required
- **Resources**: Lower requirements

**Method 2: Full Module Deployment**
- **Best for**: Production use, advanced features
- **Components**: Server + Web Interface + Database + Redis
- **Configuration**: Complete management system
- **Resources**: Higher requirements (8GB+ RAM)

### **Q: How to automatically pull the latest code and compile and start?**

See the [DevOps Integration Guide](../guides/dev-ops-integration.md) for automated deployment scripts and CI/CD setup.

### **Q: How to integrate with Nginx?**

For Nginx integration and SSL configuration, refer to [GitHub Issue #791](https://github.com/lapy/xiaozhi-esp32-server/issues/791).

## 🔌 Hardware Issues

### **Q: Which ESP32 board should I use?**

**Recommended Boards:**
- **ESP32-S3-DevKitC-1**: Official Espressif board, good for development
- **ESP32-S3-BOX**: Built-in microphone and speaker, complete solution
- **ESP32-S3-BOX-3**: Latest version with improved audio
- **ESP32-S3-Korvo-2**: Audio-focused development board

**Budget Options:**
- **ESP32-DevKitC**: Basic development board
- **ESP32-WROOM-32**: Module with development board

### **Q: How to compile ESP32 firmware myself?**

See the [Firmware Build Guide](../hardware/firmware.md) for complete instructions on:
- Setting up ESP-IDF environment
- Configuring OTA addresses
- Compiling and flashing firmware

### **Q: How to modify OTA address based on pre-compiled firmware?**

See the [Firmware Compilation Guide](../hardware/firmware.md) for instructions on:
- Using pre-compiled firmware versions 1.6.1+
- Configuring custom server addresses
- Network configuration mode setup

## 🔌 Integration Issues

### **Q: How to enable phone number registration for Smart Control Panel?**

See the [SMS Integration Guide](../guides/sms-integration.md) for Ali SMS integration setup.

### **Q: How to integrate with HomeAssistant for smart home control?**

See the [HomeAssistant Integration Guide](../guides/homeassistant.md) for three different integration methods:
1. Xiaozhi community-built HA calling function
2. Using Home Assistant's voice assistant as LLM tool
3. Using Home Assistant's MCP service (recommended)

### **Q: How to enable vision model for photo recognition?**

See the [Vision Integration Guide](../guides/vision.md) for:
- Single module mode setup
- Full module mode setup
- Camera device requirements
- Vision model configuration

### **Q: How to enable voiceprint recognition?**

See the [Voiceprint Integration Guide](../guides/voiceprint.md) for voice recognition setup and configuration.

## 📊 Performance Testing

### **Q: How to test component performance?**

See the [Performance Testing Guide](../guides/performance-testing.md) for:
- Component speed testing
- Performance optimization
- Benchmarking tools

### **Q: Where can I find performance test results?**

Check the [Xiaozhi Performance Research](https://github.com/lapy/xiaozhi-performance-research) repository for:
- Regular performance test results
- Component comparison data
- Optimization recommendations

## 🆘 Getting Help

### **Q: More questions? Contact us! 💬**

You can submit your questions in [GitHub Issues](https://github.com/lapy/xiaozhi-esp32-server/issues).

**When asking for help, please include:**
- **Operating system** and version
- **Deployment method** (Docker/local)
- **Error messages** and logs
- **Steps to reproduce** the issue
- **Hardware information** (ESP32 board type)

**Community Resources:**
- **GitHub Discussions**: Community support and questions
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and references
- **Performance Research**: Testing results and benchmarks

## 🔧 Installation & Setup

### **Q: Which installation method should I choose?**
A: 
- **Docker (Recommended)**: Easier setup, consistent environment, better for beginners
- **Local Installation**: More control, better for developers, requires more setup

### **Q: Can I run Xiaozhi on Windows/Mac/Linux?**
A: Yes! Xiaozhi supports all major operating systems:
- **Windows 10/11**: Full support with Docker Desktop
- **macOS**: Full support with Docker Desktop
- **Linux**: Full support (Ubuntu, Debian, CentOS)

### **Q: Do I need a powerful computer to run Xiaozhi?**
A: Minimum requirements:
- **CPU**: 2+ cores, 2.0+ GHz
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space

For local AI models (Whisper, LMStudio), you'll need more RAM (8GB+) and a decent CPU.

### **Q: Can I run Xiaozhi on a Raspberry Pi?**
A: Yes, but with limitations:
- **Raspberry Pi 4** (4GB+ RAM) recommended
- **Local AI models** may be slow
- **Cloud AI services** work well
- **Docker** installation recommended

## 🤖 AI Providers & Configuration

### **Q: Which AI providers should I use?**
A: It depends on your needs:

**Free Setup:**
- **ASR**: WhisperASR (local)
- **LLM**: LMStudioLLM (local)
- **TTS**: EdgeTTS (free)

**Premium Setup:**
- **ASR**: OpenAIASR (cloud)
- **LLM**: OpenAILLM (cloud)
- **TTS**: OpenAITTS (cloud)

**Hybrid Setup:**
- **ASR**: WhisperASR (local for privacy)
- **LLM**: OpenAILLM (cloud for capability)
- **TTS**: EdgeTTS (free for cost)

### **Q: How do I get API keys for AI services?**
A: 
- **OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com) → API Keys
- **Groq**: Sign up at [console.groq.com](https://console.groq.com) → API Keys
- **Azure**: Sign up at [portal.azure.com](https://portal.azure.com) → Cognitive Services

### **Q: Can I use Xiaozhi without internet?**
A: Yes! With local AI models:
- **WhisperASR**: Completely offline
- **LMStudioLLM**: Completely offline
- **EdgeTTS**: Requires internet (but you can use local TTS alternatives)

### **Q: How accurate is the speech recognition?**
A: Accuracy depends on the provider and model:
- **Whisper Large**: 95%+ accuracy in quiet environments
- **Whisper Base**: 90%+ accuracy, faster processing
- **OpenAI Whisper**: 95%+ accuracy, cloud processing

## 🔌 Hardware & ESP32

### **Q: Which ESP32 board should I buy?**
A: 
- **ESP32-S3-BOX-3**: Best overall (built-in audio, display)
- **ESP32-S3-DevKitC-1**: Best for development (external components)
- **ESP32-S3-BOX-Lite**: Budget option (built-in audio)

### **Q: Can I use other microcontrollers besides ESP32?**
A: Currently, Xiaozhi is designed specifically for ESP32. The communication protocol and firmware are ESP32-specific. Other microcontrollers would require significant modifications.

### **Q: How do I connect audio components to ESP32?**
A: 
- **Microphone**: Connect to GPIO 15-17 (I2S interface)
- **Speaker**: Connect to GPIO 18-20 (I2S interface)
- **Power**: Use 3.3V for components, GND for ground

### **Q: Can I use multiple microphones for better audio?**
A: Yes! You can configure multiple microphones for:
- **Better noise cancellation**
- **Directional audio pickup**
- **Improved accuracy**

## 🌐 Network & Connectivity

### **Q: Does Xiaozhi work over WiFi only?**
A: Yes, Xiaozhi requires WiFi connectivity for:
- **ESP32 to server communication**
- **AI service API calls** (if using cloud services)
- **OTA updates**

### **Q: Can I use Xiaozhi over cellular/4G?**
A: Yes, but you'll need:
- **ESP32 with cellular module** (ESP32-S3 + SIM800L)
- **Cellular data plan**
- **Modified firmware** for cellular communication

### **Q: What ports does Xiaozhi use?**
A: 
- **8000**: WebSocket communication (ESP32 ↔ Server)
- **8001**: Web management interface
- **8002**: REST API server
- **8003**: OTA update server

### **Q: Can I access Xiaozhi from outside my home network?**
A: Yes, but you'll need:
- **Port forwarding** on your router
- **Dynamic DNS** service (if you don't have static IP)
- **SSL/TLS** for secure connections
- **Firewall configuration**

## 🎤 Voice Interaction

### **Q: How do I change the wake word?**
A: You can customize the wake word in the configuration:
```yaml
wake_word:
  phrase: "Hello Assistant"  # Your custom wake word
  sensitivity: 0.5
```

### **Q: Can Xiaozhi understand multiple languages?**
A: Yes! Xiaozhi supports multiple languages:
- **WhisperASR**: 99+ languages
- **OpenAI**: Multiple languages
- **EdgeTTS**: Multiple voice options

Configure the language in your ASR settings.

### **Q: Why is the response slow?**
A: Response time depends on several factors:
- **AI provider** (local vs cloud)
- **Network latency**
- **Server performance**
- **Model size**

To improve speed:
- Use faster AI models
- Enable streaming processing
- Optimize network connection
- Use local AI providers

### **Q: Can I interrupt Xiaozhi while it's speaking?**
A: Yes! Xiaozhi supports interruption:
- **Say the wake word** while it's speaking
- **Configure interruption** in settings
- **Adjust sensitivity** for better detection

## 🔧 Troubleshooting

### **Q: My ESP32 won't connect to the server**
A: Check these common issues:
1. **WiFi credentials** are correct
2. **Server URL** format is correct (`ws://IP:8000/xiaozhi/v1/`)
3. **Firewall** allows connections
4. **Server is running** and accessible
5. **ESP32 firmware** is up to date

### **Q: I can't hear any audio output**
A: Troubleshoot audio issues:
1. **Check speaker connections**
2. **Verify amplifier power**
3. **Test speaker** with multimeter
4. **Check volume settings**
5. **Verify TTS provider** is working

### **Q: Speech recognition is inaccurate**
A: Improve accuracy by:
1. **Better microphone positioning**
2. **Reducing background noise**
3. **Using appropriate ASR model**
4. **Checking audio quality**
5. **Specifying language** in settings

### **Q: The server keeps crashing**
A: Common causes and solutions:
1. **Out of memory**: Increase RAM or use smaller models
2. **Database issues**: Check MySQL/PostgreSQL status
3. **Port conflicts**: Check for conflicting services
4. **Configuration errors**: Validate config files
5. **Dependency issues**: Reinstall requirements

## 💰 Cost & Billing

### **Q: How much does it cost to run Xiaozhi?**
A: Costs vary by setup:

**Free Setup:**
- **Hardware**: $20-50 (ESP32 + components)
- **Software**: Free (local AI models)
- **Total**: $20-50 one-time

**Premium Setup:**
- **Hardware**: $20-50 (ESP32 + components)
- **AI Services**: $5-20/month (OpenAI, etc.)
- **Total**: $20-50 + $5-20/month

### **Q: Are there any hidden costs?**
A: No hidden costs! You only pay for:
- **Hardware** (one-time purchase)
- **AI services** (if using cloud providers)
- **Internet connection** (you already have this)

### **Q: Can I reduce AI service costs?**
A: Yes! Several strategies:
- **Use local AI models** (Whisper, LMStudio)
- **Optimize API usage** (shorter responses, fewer calls)
- **Use free tiers** (OpenAI free credits)
- **Cache responses** (avoid duplicate API calls)

## 🔒 Security & Privacy

### **Q: Is my data secure with Xiaozhi?**
A: Xiaozhi offers multiple security options:
- **Local processing** (data never leaves your device)
- **Encrypted communication** (WebSocket over TLS)
- **Secure API keys** (environment variables)
- **User authentication** (web interface)

### **Q: Can I use Xiaozhi without sending data to cloud services?**
A: Yes! Use local AI models:
- **WhisperASR**: Completely local
- **LMStudioLLM**: Completely local
- **Local TTS**: Various options available

### **Q: How do I secure my Xiaozhi installation?**
A: Security best practices:
- **Use strong passwords** for all accounts
- **Enable HTTPS** for web interface
- **Restrict network access** (firewall rules)
- **Regular updates** (keep software current)
- **Monitor access logs** (check for suspicious activity)

## 🚀 Advanced Features

### **Q: Can I integrate Xiaozhi with HomeAssistant?**
A: Yes! Xiaozhi has built-in HomeAssistant integration:
- **Voice control** of HomeAssistant devices
- **Function calling** for automation
- **Real-time status** updates
- **Custom commands** for specific devices

### **Q: Can I create custom plugins for Xiaozhi?**
A: Yes! Xiaozhi supports custom plugins:
- **Python-based** plugin system
- **Function calling** integration
- **Custom responses** and behaviors
- **Third-party service** integration

### **Q: Does Xiaozhi support MQTT?**
A: Yes! Xiaozhi includes MQTT support:
- **Publish/subscribe** to MQTT topics
- **Voice-controlled** MQTT commands
- **Device status** monitoring
- **Integration** with IoT devices

### **Q: Can I use Xiaozhi for commercial purposes?**
A: Yes! Xiaozhi is open source (MIT license):
- **Commercial use** allowed
- **Modification** allowed
- **Distribution** allowed
- **Private use** allowed

## 🆘 Getting Help

### **Q: Where can I get help if I'm stuck?**
A: Multiple support options:
- **Documentation**: Comprehensive guides and references
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Community support and questions
- **Troubleshooting Guide**: Common issues and solutions

### **Q: How do I report a bug?**
A: Report bugs on GitHub:
1. **Check existing issues** first
2. **Create new issue** with detailed description
3. **Include logs** and error messages
4. **Provide system information** (OS, hardware, etc.)
5. **Describe steps** to reproduce the issue

### **Q: Can I contribute to Xiaozhi development?**
A: Yes! We welcome contributions:
- **Code contributions** (bug fixes, features)
- **Documentation improvements**
- **Testing and feedback**
- **Community support**

See our [Contributing Guide](contributing.md) for details.

### **Q: Is there a community forum or Discord?**
A: Yes! Join our community:
- **GitHub Discussions**: [github.com/lapy/xiaozhi-esp32-server/discussions](https://github.com/lapy/xiaozhi-esp32-server/discussions)
- **Issues**: [github.com/lapy/xiaozhi-esp32-server/issues](https://github.com/lapy/xiaozhi-esp32-server/issues)

---

## 🎯 Still Need Help?

If you didn't find the answer to your question:

1. **Check [Troubleshooting Guide](troubleshooting.md)** for common issues
2. **Search [GitHub Issues](https://github.com/lapy/xiaozhi-esp32-server/issues)** for similar problems
3. **Ask in [GitHub Discussions](https://github.com/lapy/xiaozhi-esp32-server/discussions)** for community help
4. **Create a new issue** if you found a bug

---

**Happy building! 🚀**
