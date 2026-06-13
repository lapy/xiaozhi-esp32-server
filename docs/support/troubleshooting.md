# 🛠️ Troubleshooting Guide

This comprehensive troubleshooting guide helps you diagnose and fix common issues with Xiaozhi ESP32 Server. Follow the steps systematically to resolve problems quickly.

## 🔍 Diagnostic Tools

### **Health Check Commands**

```bash
# Check server status
curl http://localhost:8000/health

# Check web interface
curl http://localhost:8001

# Check API server
curl http://localhost:8002/api/health

# Check OTA interface
curl http://localhost:8003/xiaozhi/ota/

# Check Docker services
docker-compose ps

# Check system resources
htop
df -h
free -h
```

### **Log Analysis**

```bash
# View server logs
docker-compose logs -f xiaozhi-server

# View specific service logs
docker-compose logs -f manager-api
docker-compose logs -f manager-web

# View system logs
sudo journalctl -u xiaozhi-server -f

# Check error logs
tail -f logs/error.log
```

## 🚀 Server Issues

### **Server Won't Start**

#### **Symptoms**
- Server fails to start
- Error messages during startup
- Services not responding

#### **Diagnosis Steps**

1. **Check Docker Status**
```bash
# Check Docker is running
docker --version
docker-compose --version

# Check Docker services
docker-compose ps
```

2. **Check Port Conflicts**
```bash
# Check if ports are in use
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :8003
```

3. **Check System Resources**
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top
```

#### **Solutions**

**Port Conflicts:**
```bash
# Kill processes using ports
sudo fuser -k 8000/tcp
sudo fuser -k 8001/tcp
sudo fuser -k 8002/tcp
sudo fuser -k 8003/tcp

# Or change ports in docker-compose.yml
ports:
  - "8000:8000"  # Change first number
```

**Memory Issues:**
```bash
# Increase Docker memory limit
# In Docker Desktop: Settings → Resources → Memory

# Or use smaller AI models
ASR:
  WhisperASR:
    model_name: tiny  # Instead of large
```

**Docker Issues:**
```bash
# Restart Docker
sudo systemctl restart docker

# Clean up Docker
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### **Server Crashes Frequently**

#### **Symptoms**
- Server stops responding
- Frequent restarts
- Error messages in logs

#### **Diagnosis Steps**

1. **Check Logs for Errors**
```bash
# View recent logs
docker-compose logs --tail=100 xiaozhi-server

# Look for specific errors
grep -i "error\|exception\|crash" logs/xiaozhi-server.log
```

2. **Check Resource Usage**
```bash
# Monitor resource usage
docker stats

# Check for memory leaks
ps aux | grep python
```

3. **Check Configuration**
```bash
# Validate configuration
python -c "import yaml; yaml.safe_load(open('data/.config.yaml'))"

# Check environment variables
env | grep -E "(DB_|REDIS_|OPENAI_)"
```

#### **Solutions**

**Memory Issues:**
```yaml
# Optimize memory usage
performance:
  streaming: true
  parallel_processing: false
  cache_responses: true
  preload_models: false
```

**Configuration Errors:**
```bash
# Reset configuration
cp data/.config.yaml data/.config.yaml.backup
# Edit configuration file
nano data/.config.yaml
```

**Database Issues:**
```bash
# Check database connection
mysql -u xiaozhi -p -h localhost xiaozhi

# Restart database
docker-compose restart mysql
```

## 🔌 ESP32 Connection Issues

### **ESP32 Won't Connect**

#### **Symptoms**
- ESP32 doesn't appear in OTA interface
- WebSocket connection fails
- Device shows offline status

#### **Diagnosis Steps**

1. **Check Network Connectivity**
```bash
# Test ESP32 connectivity
ping ESP32_IP_ADDRESS

# Check WiFi signal strength
# On ESP32: Check WiFi.status() in serial monitor
```

2. **Check WebSocket URL**
```bash
# Verify WebSocket URL format
# Should be: ws://SERVER_IP:8000/xiaozhi/v1/
# Check in OTA interface: http://localhost:8003/xiaozhi/ota/
```

3. **Check Server Logs**
```bash
# Look for connection attempts
docker-compose logs -f xiaozhi-server | grep -i "websocket\|connect"
```

#### **Solutions**

**Network Issues:**
```bash
# Check firewall rules
sudo ufw status
sudo iptables -L

# Allow WebSocket connections
sudo ufw allow 8000
```

**WebSocket URL Issues:**
```bash
# Update WebSocket URL in ESP32 firmware
# Use correct server IP address
# Format: ws://192.168.1.100:8000/xiaozhi/v1/
```

**ESP32 Firmware Issues:**
```bash
# Reflash ESP32 firmware
# Download latest firmware from OTA interface
# Use esptool.py to flash
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 firmware.bin
```

### **ESP32 Connects But No Audio**

#### **Symptoms**
- ESP32 shows connected
- No audio input/output
- Voice commands not working

#### **Diagnosis Steps**

1. **Check Audio Configuration**
```bash
# Check audio settings in web interface
# Go to: http://localhost:8001 → Devices → Your Device
```

2. **Test Audio Components**
```bash
# Test microphone
# Check connections: GPIO 15-17
# Verify power: 3.3V, GND

# Test speaker
# Check connections: GPIO 18-20
# Verify amplifier power
```

3. **Check Audio Processing**
```bash
# Test ASR provider
curl -X POST http://localhost:8000/api/test/asr \
  -H "Content-Type: application/json" \
  -d '{"audio_file": "test.wav"}'
```

#### **Solutions**

**Microphone Issues:**
```yaml
# Check microphone configuration
audio:
  input:
    sample_rate: 16000
    channels: 1
    bit_depth: 16
    buffer_size: 1024
    noise_reduction: true
```

**Speaker Issues:**
```yaml
# Check speaker configuration
audio:
  output:
    sample_rate: 22050
    channels: 1
    bit_depth: 16
    buffer_size: 1024
    volume: 0.8
```

**Audio Processing Issues:**
```bash
# Restart audio services
docker-compose restart xiaozhi-server

# Check audio dependencies
pip list | grep -E "(whisper|edge-tts|pyaudio)"
```

## 🤖 AI Provider Issues

### **Speech Recognition Not Working**

#### **Symptoms**
- No speech recognition
- Poor accuracy
- Timeout errors

#### **Diagnosis Steps**

1. **Test ASR Provider**
```bash
# Test WhisperASR
curl -X POST http://localhost:8000/api/test/asr \
  -H "Content-Type: application/json" \
  -d '{"provider": "WhisperASR", "audio_file": "test.wav"}'

# Test OpenAIASR
curl -X POST http://localhost:8000/api/test/asr \
  -H "Content-Type: application/json" \
  -d '{"provider": "OpenAIASR", "audio_file": "test.wav"}'
```

2. **Check Model Files**
```bash
# Check Whisper models
ls -la models/whisper/
# Should see: tiny, base, small, medium, large

# Check model integrity
python -c "import whisper; whisper.load_model('base')"
```

3. **Check API Keys**
```bash
# Test OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### **Solutions**

**Model Issues:**
```bash
# Reinstall Whisper models
pip uninstall whisper
pip install openai-whisper

# Download models
python -c "import whisper; whisper.load_model('base')"
```

**API Key Issues:**
```bash
# Set API key
export OPENAI_API_KEY=your_api_key_here

# Or add to .env file
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

**Accuracy Issues:**
```yaml
# Optimize ASR settings
ASR:
  WhisperASR:
    model_name: large        # Use larger model
    language: en            # Specify language
    temperature: 0.0        # Reduce randomness
    compression_ratio_threshold: 2.4
    logprob_threshold: -1.0
    no_speech_threshold: 0.6
```

### **Language Model Not Responding**

#### **Symptoms**
- No responses to voice commands
- Timeout errors
- Poor response quality

#### **Diagnosis Steps**

1. **Test LLM Provider**
```bash
# Test OpenAI LLM
curl -X POST http://localhost:8000/api/test/llm \
  -H "Content-Type: application/json" \
  -d '{"provider": "OpenAILLM", "message": "Hello"}'

# Test LMStudio LLM
curl -X POST http://localhost:8000/api/test/llm \
  -H "Content-Type: application/json" \
  -d '{"provider": "LMStudioLLM", "message": "Hello"}'
```

2. **Check LLM Configuration**
```bash
# Check LLM settings in web interface
# Go to: http://localhost:8001 → Model Configuration → LLM
```

3. **Check Network Connectivity**
```bash
# Test OpenAI API
curl https://api.openai.com/v1/models

# Test LMStudio
curl http://localhost:1234/v1/models
```

#### **Solutions**

**OpenAI Issues:**
```bash
# Check API key and billing
# Go to: https://platform.openai.com/usage

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

**LMStudio Issues:**
```bash
# Check LMStudio is running
curl http://localhost:1234/v1/models

# Restart LMStudio
# Load a model and enable local API
```

**Response Quality Issues:**
```yaml
# Optimize LLM settings
LLM:
  OpenAILLM:
    model_name: gpt-4o-mini    # Use appropriate model
    temperature: 0.7           # Balance creativity
    max_tokens: 1000          # Sufficient length
    top_p: 1.0                # Use full vocabulary
```

### **Text-to-Speech Not Working**

#### **Symptoms**
- No audio output
- TTS errors
- Poor audio quality

#### **Diagnosis Steps**

1. **Test TTS Provider**
```bash
# Test EdgeTTS
curl -X POST http://localhost:8000/api/test/tts \
  -H "Content-Type: application/json" \
  -d '{"provider": "EdgeTTS", "text": "Hello"}'

# Test OpenAI TTS
curl -X POST http://localhost:8000/api/test/tts \
  -H "Content-Type: application/json" \
  -d '{"provider": "OpenAITTS", "text": "Hello"}'
```

2. **Check Audio Output**
```bash
# Test speaker connections
# Check GPIO 18-20 connections
# Verify amplifier power
```

3. **Check TTS Configuration**
```bash
# Check TTS settings in web interface
# Go to: http://localhost:8001 → Model Configuration → TTS
```

#### **Solutions**

**EdgeTTS Issues:**
```bash
# Install EdgeTTS
pip install edge-tts

# Test EdgeTTS
python -c "import edge_tts; print('EdgeTTS installed')"
```

**OpenAI TTS Issues:**
```bash
# Check API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Test TTS API
curl -X POST https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "tts-1", "input": "Hello", "voice": "alloy"}'
```

**Audio Quality Issues:**
```yaml
# Optimize TTS settings
TTS:
  EdgeTTS:
    voice: en-US-AriaNeural    # Use high-quality voice
    rate: +0%                  # Normal speech rate
    pitch: +0Hz                # Normal pitch
    volume: +0%                # Normal volume
```

## 🌐 Network Issues

### **WebSocket Connection Problems**

#### **Symptoms**
- ESP32 can't connect to server
- Intermittent disconnections
- Connection timeouts

#### **Diagnosis Steps**

1. **Check Network Connectivity**
```bash
# Test server accessibility
ping SERVER_IP_ADDRESS

# Test WebSocket port
telnet SERVER_IP_ADDRESS 8000
```

2. **Check Firewall Rules**
```bash
# Check firewall status
sudo ufw status

# Check iptables rules
sudo iptables -L
```

3. **Check WebSocket URL**
```bash
# Verify URL format
# Should be: ws://IP:8000/xiaozhi/v1/
# Check in OTA interface
```

#### **Solutions**

**Firewall Issues:**
```bash
# Allow WebSocket port
sudo ufw allow 8000

# Allow all Xiaozhi ports
sudo ufw allow 8000:8003
```

**Network Configuration:**
```bash
# Check network interface
ip addr show

# Check routing table
ip route show

# Test DNS resolution
nslookup SERVER_IP_ADDRESS
```

**WebSocket URL Issues:**
```bash
# Use correct IP address
# Find server IP: ip addr show
# Update ESP32 firmware with correct URL
```

### **Slow Response Times**

#### **Symptoms**
- Delayed responses
- High latency
- Timeout errors

#### **Diagnosis Steps**

1. **Check Network Latency**
```bash
# Test ping latency
ping -c 10 SERVER_IP_ADDRESS

# Test WebSocket latency
# Use browser developer tools
```

2. **Check Server Performance**
```bash
# Monitor server resources
docker stats

# Check server logs for performance issues
docker-compose logs -f xiaozhi-server | grep -i "slow\|timeout"
```

3. **Check AI Provider Performance**
```bash
# Test AI provider response times
time curl -X POST http://localhost:8000/api/test/llm \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

#### **Solutions**

**Network Optimization:**
```bash
# Optimize network settings
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
sysctl -p
```

**Server Optimization:**
```yaml
# Optimize server performance
performance:
  streaming: true
  parallel_processing: true
  cache_responses: true
  preload_models: true
  gpu_acceleration: true
```

**AI Provider Optimization:**
```yaml
# Use faster AI models
ASR:
  WhisperASR:
    model_name: base        # Instead of large

LLM:
  OpenAILLM:
    model_name: gpt-4o-mini # Instead of gpt-4o
    max_tokens: 500         # Shorter responses
```

## 🔧 Configuration Issues

### **Configuration File Errors**

#### **Symptoms**
- Server won't start
- Configuration errors in logs
- Settings not applied

#### **Diagnosis Steps**

1. **Validate Configuration**
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('data/.config.yaml'))"

# Check JSON syntax
python -c "import json; json.load(open('data/.config.json'))"
```

2. **Check Configuration Permissions**
```bash
# Check file permissions
ls -la data/.config.yaml

# Check file ownership
stat data/.config.yaml
```

3. **Check Configuration Content**
```bash
# View configuration
cat data/.config.yaml

# Check for syntax errors
grep -n ":" data/.config.yaml
```

#### **Solutions**

**Syntax Errors:**
```bash
# Fix YAML syntax
# Use online YAML validator
# Check indentation (use spaces, not tabs)

# Example correct syntax:
ASR:
  WhisperASR:
    type: whisper
    model_name: base
```

**Permission Issues:**
```bash
# Fix permissions
sudo chown $USER:$USER data/.config.yaml
sudo chmod 644 data/.config.yaml
```

**Content Issues:**
```bash
# Reset configuration
cp data/.config.yaml data/.config.yaml.backup
# Edit configuration file
nano data/.config.yaml
```

### **Environment Variable Issues**

#### **Symptoms**
- API keys not working
- Database connection failures
- Service configuration errors

#### **Diagnosis Steps**

1. **Check Environment Variables**
```bash
# Check all environment variables
env | grep -E "(DB_|REDIS_|OPENAI_)"

# Check specific variables
echo $OPENAI_API_KEY
echo $DB_HOST
echo $REDIS_HOST
```

2. **Check .env File**
```bash
# Check .env file exists
ls -la .env

# Check .env content
cat .env
```

3. **Test Environment Loading**
```bash
# Test environment loading
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### **Solutions**

**Missing Variables:**
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=3306
DB_NAME=xiaozhi
DB_USER=xiaozhi
DB_PASSWORD=your_password
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
```

**Incorrect Variables:**
```bash
# Update .env file
nano .env

# Restart services
docker-compose restart
```

**Loading Issues:**
```bash
# Source .env file
source .env

# Or restart shell
exec $SHELL
```

## 🆘 Emergency Recovery

### **Complete System Reset**

If nothing else works, you can reset the entire system:

```bash
# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v
docker system prune -a

# Remove data directory
rm -rf data/

# Recreate data directory
mkdir -p data

# Restart services
docker-compose up -d
```

### **Configuration Reset**

Reset only the configuration:

```bash
# Backup current configuration
cp data/.config.yaml data/.config.yaml.backup

# Reset to defaults
cat > data/.config.yaml << EOF
# Default configuration
selected_module:
  ASR: WhisperASR
  LLM: LMStudioLLM
  TTS: EdgeTTS

ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: null

LLM:
  LMStudioLLM:
    type: openai
    base_url: http://localhost:1234/v1
    api_key: lm-studio
    model_name: llama3.1:8b

TTS:
  EdgeTTS:
    type: edge_tts
    voice: en-US-AriaNeural
    rate: +0%
    pitch: +0Hz
    volume: +0%
EOF

# Restart services
docker-compose restart
```

### **Database Reset**

Reset the database:

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm xiaozhi-esp32-server_mysql_data

# Restart services
docker-compose up -d

# Wait for database initialization
sleep 30

# Check database status
docker-compose logs mysql
```

## 📞 Getting Help

### **When to Ask for Help**

Ask for help when:
- You've tried all troubleshooting steps
- You're getting error messages you don't understand
- The issue is preventing you from using Xiaozhi
- You suspect a bug in the software

### **How to Ask for Help**

1. **Gather Information**
   - Error messages and logs
   - System information (OS, hardware)
   - Configuration files
   - Steps to reproduce the issue

2. **Create GitHub Issue**
   - Go to [GitHub Issues](https://github.com/lapy/xiaozhi-esp32-server/issues)
   - Click "New Issue"
   - Fill out the issue template
   - Attach relevant files and logs

3. **Join Community Discussion**
   - Go to [GitHub Discussions](https://github.com/lapy/xiaozhi-esp32-server/discussions)
   - Search for similar issues
   - Ask questions in the community

### **Information to Include**

When asking for help, include:
- **Operating system** and version
- **Hardware** (ESP32 board, computer specs)
- **Installation method** (Docker, local)
- **Error messages** and logs
- **Steps to reproduce** the issue
- **What you've tried** already

---

## 🎯 Quick Reference

### **Essential Commands**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check health
curl http://localhost:8000/health
```

### **Common Solutions**
- **Port conflicts**: Kill processes or change ports
- **Memory issues**: Use smaller models or increase RAM
- **Network issues**: Check firewall and connectivity
- **Configuration errors**: Validate syntax and permissions

### **Emergency Recovery**
- **System reset**: `docker-compose down -v && docker system prune -a`
- **Config reset**: Restore from backup or recreate
- **Database reset**: Remove volume and restart

---

**Most issues can be resolved with these troubleshooting steps! 🛠️**

👉 **[Next: Community Support →](community.md)**
