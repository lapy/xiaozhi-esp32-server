# ⚙️ Configuration Reference

This guide provides a complete reference for all configuration options available in Xiaozhi ESP32 Server.

## 🎯 Configuration Overview

Xiaozhi uses YAML configuration files with the following structure:
- **Main configuration**: `data/.config.yaml`
- **Plugin configurations**: `plugins/*/config.yaml`
- **Environment variables**: Override configuration values

## 📋 Configuration Schema

### **Root Level Configuration**

```yaml
# Server Configuration
server:
  websocket: ws://YOUR_IP:8000/xiaozhi/v1/
  ota: http://YOUR_IP:8003/xiaozhi/ota/
  host: 0.0.0.0
  port: 8000
  ssl:
    enabled: false
    cert_file: /path/to/cert.pem
    key_file: /path/to/key.pem

# AI Module Selection
selected_module:
  VAD: SileroVAD
  ASR: WhisperASR
  LLM: LMStudioLLM
  VLLM: OpenAILLMVLLM
  TTS: EdgeTTS

# AI Provider Configurations
ASR: {}
LLM: {}
TTS: {}
VLLM: {}

# Voice Activity Detection
VAD: {}

# Memory Configuration
memory: {}

# Plugin System
plugins: {}

# Performance Settings
performance: {}

# Security Settings
security: {}

# Logging Configuration
logging: {}

# Monitoring
monitoring: {}
```

## 🔧 Server Configuration

### **Basic Server Settings**

```yaml
server:
  # WebSocket endpoint for ESP32 devices
  websocket: ws://YOUR_IP:8000/xiaozhi/v1/
  
  # OTA (Over-the-Air) update endpoint
  ota: http://YOUR_IP:8003/xiaozhi/ota/
  
  # Server host and port
  host: 0.0.0.0
  port: 8000
  
  # SSL/TLS configuration
  ssl:
    enabled: false
    cert_file: /path/to/cert.pem
    key_file: /path/to/key.pem
    verify_certificates: true
  
  # CORS settings
  cors:
    enabled: true
    allowed_origins:
      - "http://localhost:3000"
      - "https://yourdomain.com"
    allowed_methods:
      - GET
      - POST
      - PUT
      - DELETE
    allowed_headers:
      - Content-Type
      - Authorization
      - X-API-Key
```

### **Advanced Server Settings**

```yaml
server:
  # Connection limits
  max_connections: 100
  max_connections_per_ip: 10
  connection_timeout: 300
  
  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60
    burst_size: 10
  
  # API authentication
  api_auth:
    enabled: true
    api_key: your-secure-api-key
    header_name: X-API-Key
  
  # WebSocket settings
  websocket:
    ping_interval: 30
    ping_timeout: 10
    max_message_size: 1048576  # 1MB
    compression: true
```

## 🤖 AI Provider Configuration

### **Speech Recognition (ASR)**

#### **WhisperASR**
```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base          # tiny, base, small, medium, large-v1, large-v2, large-v3
    device: auto             # auto, cpu, cuda
    language: null           # null for auto-detect, or specific language code
    output_dir: tmp/
    streaming: false
    chunk_length: 30
    overlap: 2
    compute_type: float16     # float16, float32
    batch_size: 1
```

#### **OpenAI ASR**
```yaml
ASR:
  OpenAIASR:
    type: openai
    api_key: your-openai-api-key
    model: whisper-1
    language: en
    temperature: 0.0
    timeout: 30
    retry_count: 3
    retry_delay: 1
```

#### **VoskASR**
```yaml
ASR:
  VoskASR:
    type: vosk
    model_path: models/vosk/vosk-model-en-us-0.22
    output_dir: tmp/
    sample_rate: 16000
    language: en
    partial_words: true
    max_alternatives: 0
```

### **Large Language Model (LLM)**

#### **LMStudioLLM**
```yaml
LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
    streaming: false
    gpu_layers: 35
    context_length: 4096
    top_p: 0.9
    top_k: 40
    repeat_penalty: 1.1
```

#### **OpenAI LLM**
```yaml
LLM:
  OpenAILLM:
    type: openai
    api_key: your-openai-api-key
    model: gpt-4o-mini
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
    streaming: false
    top_p: 0.9
    frequency_penalty: 0.0
    presence_penalty: 0.0
```

#### **OllamaLLM**
```yaml
LLM:
  OllamaLLM:
    type: ollama
    base_url: http://localhost:11434
    model_name: llama3.1:8b
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
    streaming: false
    context_length: 4096
```

### **Text-to-Speech (TTS)**

#### **EdgeTTS**
```yaml
TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural
    rate: 1.0
    volume: 1.0
    output_dir: tmp/
    format: wav
    sample_rate: 22050
    bit_depth: 16
    channels: 1
```

#### **OpenAI TTS**
```yaml
TTS:
  OpenAITTS:
    type: openai
    api_key: your-openai-api-key
    model: tts-1
    voice: alloy              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0
    output_dir: tmp/
    format: mp3
    quality: standard
```

#### **ElevenLabs TTS**
```yaml
TTS:
  ElevenLabsTTS:
    type: elevenlabs
    api_key: your-elevenlabs-api-key
    voice_id: pNInz6obpgDQGcFmaJgB
    model_id: eleven_monolingual_v1
    voice_settings:
      stability: 0.5
      similarity_boost: 0.5
    output_dir: tmp/
    format: mp3
```

### **Vision Language Model (VLLM)**

#### **OpenAI VLLM**
```yaml
VLLM:
  OpenAILLMVLLM:
    type: openai
    api_key: your-openai-api-key
    model: gpt-4o
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
    vision_enabled: true
    max_image_size: 1024
    supported_formats: [jpg, png, gif, webp]
```

## 🎤 Voice Activity Detection (VAD)

### **SileroVAD**
```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700
    pre_padding_ms: 300
    post_padding_ms: 300
    window_size: 512
    hop_length: 256
    min_speech_duration_ms: 250
    max_speech_duration_ms: 30000
    sample_rate: 16000
```

### **WebRTC VAD**
```yaml
VAD:
  WebRTCVAD:
    mode: 3                   # 0, 1, 2, 3 (aggressiveness)
    sample_rate: 16000
    frame_duration_ms: 30
    min_silence_duration_ms: 700
    pre_padding_ms: 300
    post_padding_ms: 300
```

## 🧠 Memory Configuration

### **Local Short-term Memory**
```yaml
memory:
  mem_local_short:
    type: local_short
    max_messages: 20
    max_age_hours: 24
    cleanup_interval: 3600
    storage_path: data/memory/
    compression: true
```

### **Local Long-term Memory**
```yaml
memory:
  mem_local_long:
    type: local_long
    storage_path: data/memory/
    max_entries: 1000
    similarity_threshold: 0.8
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
    vector_dimension: 384
    index_type: faiss
```

### **Redis Memory**
```yaml
memory:
  mem_redis:
    type: redis
    host: localhost
    port: 6379
    password: your-redis-password
    db: 0
    max_messages: 100
    max_age_hours: 168
    key_prefix: xiaozhi:memory:
```

## 🔌 Plugin Configuration

### **Plugin System**
```yaml
plugins:
  enabled: true
  plugin_dir: plugins/
  auto_load: true
  hot_reload: false
  
  # Plugin-specific configurations
  weather:
    enabled: true
    api_key: your-weather-api-key
    default_location: "New York, NY"
    units: metric
    cache_duration: 300
  
  news:
    enabled: true
    api_key: your-news-api-key
    sources: ["bbc-news", "cnn", "reuters"]
    categories: ["technology", "science", "health"]
    max_articles: 10
  
  homeassistant:
    enabled: true
    url: http://homeassistant.local:8123
    api_key: your-ha-api-key
    entities:
      lights: [light.living_room, light.kitchen]
      switches: [switch.coffee_maker, switch.tv]
      sensors: [sensor.temperature, sensor.humidity]
```

## ⚡ Performance Configuration

### **Streaming Settings**
```yaml
performance:
  streaming:
    enabled: true
    buffer_size: 1024
    chunk_size: 512
    compression: true
  
  # Model caching
  model_cache:
    enabled: true
    cache_dir: models/cache/
    max_cache_size: 5000      # MB
    cleanup_interval: 3600    # seconds
  
  # Audio processing
  audio:
    sample_rate: 16000
    channels: 1
    bit_depth: 16
    buffer_size: 4096
    chunk_size: 1024
    gain: 1.0
  
  # GPU acceleration
  gpu:
    enabled: true
    device: auto              # auto, cpu, cuda
    memory_fraction: 0.8
    allow_growth: true
```

### **Optimization Settings**
```yaml
performance:
  # Parallel processing
  parallel:
    enabled: true
    max_workers: 4
    thread_pool_size: 8
  
  # Connection pooling
  connection_pool:
    enabled: true
    max_connections: 100
    max_keepalive: 10
    timeout: 30
  
  # Request batching
  batching:
    enabled: true
    batch_size: 10
    batch_timeout: 0.1
```

## 🔐 Security Configuration

### **Authentication**
```yaml
security:
  # API authentication
  api_auth:
    enabled: true
    api_key: your-secure-api-key
    header_name: X-API-Key
    token_expiry: 3600
    refresh_token_expiry: 86400
  
  # JWT authentication
  jwt:
    enabled: false
    secret_key: your-jwt-secret
    algorithm: HS256
    token_expiry: 3600
    refresh_token_expiry: 86400
  
  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60
    burst_size: 10
    window_size: 60
```

### **Data Encryption**
```yaml
security:
  # Data encryption
  encryption:
    enabled: true
    algorithm: AES-256-GCM
    key_file: /path/to/encryption.key
    key_rotation: 86400
  
  # Audio encryption
  audio_encryption:
    enabled: false
    algorithm: AES-128-CBC
    key_file: /path/to/audio.key
  
  # Database encryption
  database_encryption:
    enabled: false
    algorithm: AES-256-GCM
    key_file: /path/to/db.key
```

## 📊 Logging Configuration

### **Basic Logging**
```yaml
logging:
  level: INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # Log files
  files:
    main: logs/xiaozhi.log
    error: logs/error.log
    access: logs/access.log
  
  # Log rotation
  rotation:
    max_size: 10MB
    backup_count: 5
    when: midnight
```

### **Advanced Logging**
```yaml
logging:
  # Component-specific logging
  components:
    ASR:
      level: DEBUG
      file: logs/asr.log
    LLM:
      level: INFO
      file: logs/llm.log
    TTS:
      level: INFO
      file: logs/tts.log
    VAD:
      level: DEBUG
      file: logs/vad.log
  
  # Console logging
  console:
    enabled: true
    level: INFO
    colorize: true
  
  # Remote logging
  remote:
    enabled: false
    endpoint: https://logs.example.com/api/logs
    api_key: your-logging-api-key
    batch_size: 100
    flush_interval: 30
```

## 📈 Monitoring Configuration

### **Basic Monitoring**
```yaml
monitoring:
  enabled: true
  
  # Metrics collection
  metrics:
    response_time: true
    memory_usage: true
    cpu_usage: true
    audio_processing_time: true
    model_inference_time: true
  
  # Health checks
  health_checks:
    enabled: true
    interval: 30
    timeout: 10
    
    checks:
      - name: database
        type: database
        query: "SELECT 1"
      
      - name: redis
        type: redis
        command: "PING"
      
      - name: ai_models
        type: model_health
        models: [ASR, LLM, TTS]
```

### **Advanced Monitoring**
```yaml
monitoring:
  # Performance metrics
  performance:
    enabled: true
    metrics_endpoint: /metrics
    update_interval: 1
    retention_days: 30
  
  # Alerting
  alerts:
    enabled: true
    
    # Email alerts
    email:
      smtp_server: smtp.gmail.com
      smtp_port: 587
      username: alerts@yourdomain.com
      password: your-app-password
      recipients:
        - admin@yourdomain.com
        - devops@yourdomain.com
    
    # Webhook alerts
    webhooks:
      - name: slack
        url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
        events: [error, warning, critical]
      
      - name: discord
        url: https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
        events: [error, critical]
    
    # Alert conditions
    conditions:
      - name: high_response_time
        metric: response_time
        threshold: 5.0
        operator: greater_than
      
      - name: low_memory
        metric: memory_usage
        threshold: 90
        operator: greater_than
```

## 🌐 Network Configuration

### **Proxy Settings**
```yaml
network:
  # HTTP proxy
  http_proxy:
    enabled: false
    host: proxy.company.com
    port: 8080
    username: proxy_user
    password: proxy_password
  
  # HTTPS proxy
  https_proxy:
    enabled: false
    host: proxy.company.com
    port: 8080
    username: proxy_user
    password: proxy_password
  
  # Proxy bypass
  no_proxy:
    - localhost
    - 127.0.0.1
    - *.local
    - 192.168.*
```

### **Load Balancing**
```yaml
network:
  # Load balancing
  load_balancer:
    enabled: false
    
    # AI model load balancing
    ai_models:
      ASR:
        strategy: round_robin
        instances:
          - url: http://asr-1:8000
            weight: 1
          - url: http://asr-2:8000
            weight: 1
      
      LLM:
        strategy: least_connections
        instances:
          - url: http://llm-1:8000
            weight: 2
          - url: http://llm-2:8000
            weight: 1
    
    # Health checks
    health_check:
      interval: 30
      timeout: 10
      retries: 3
```

## 🔄 Backup Configuration

### **Backup Settings**
```yaml
backup:
  enabled: true
  
  # Backup schedule
  schedule:
    daily: true
    time: "02:00"
    retention_days: 30
  
  # Backup locations
  locations:
    - type: local
      path: /backups/xiaozhi/
    
    - type: s3
      bucket: xiaozhi-backups
      region: us-west-2
      access_key: your-s3-access-key
      secret_key: your-s3-secret-key
  
  # Backup content
  content:
    config_files: true
    model_files: true
    database: true
    logs: true
    audio_cache: false
```

## 🎯 Environment Variables

### **Override Configuration with Environment Variables**

```bash
# Server settings
export XIAOZHI_SERVER_HOST=0.0.0.0
export XIAOZHI_SERVER_PORT=8000
export XIAOZHI_WEBSOCKET_URL=ws://YOUR_IP:8000/xiaozhi/v1/

# AI provider settings
export OPENAI_API_KEY=your-openai-api-key
export LMSTUDIO_BASE_URL=http://localhost:1234/v1
export LMSTUDIO_MODEL_NAME=llama-3.1:8b

# Security settings
export XIAOZHI_API_KEY=your-secure-api-key
export XIAOZHI_JWT_SECRET=your-jwt-secret

# Database settings
export XIAOZHI_DB_HOST=localhost
export XIAOZHI_DB_PORT=5432
export XIAOZHI_DB_NAME=xiaozhi
export XIAOZHI_DB_USER=xiaozhi
export XIAOZHI_DB_PASSWORD=your-db-password

# Redis settings
export XIAOZHI_REDIS_HOST=localhost
export XIAOZHI_REDIS_PORT=6379
export XIAOZHI_REDIS_PASSWORD=your-redis-password
```

## 🛠️ Configuration Validation

### **Validation Rules**

```yaml
# Configuration validation
validation:
  # Required fields
  required_fields:
    - server.websocket
    - server.ota
    - selected_module.ASR
    - selected_module.LLM
    - selected_module.TTS
  
  # Field validation
  field_validation:
    server.port:
      type: integer
      min: 1
      max: 65535
    
    server.websocket:
      type: string
      pattern: "^ws://.*:.*/.*"
    
    selected_module.ASR:
      type: string
      enum: [WhisperASR, OpenAIASR, VoskASR]
    
    selected_module.LLM:
      type: string
      enum: [LMStudioLLM, OpenAILLM, OllamaLLM]
    
    selected_module.TTS:
      type: string
      enum: [EdgeTTS, OpenAITTS, ElevenLabsTTS]
```

## 🎯 Next Steps

After configuring Xiaozhi:

1. **[Test Your Configuration](../getting-started/first-device.md)** - Verify everything works
2. **[Advanced Configuration](../configuration/advanced.md)** - Fine-tune settings
3. **[Monitor Performance](../guides/monitoring.md)** - Track system health
4. **[Troubleshoot Issues](../support/troubleshooting.md)** - Fix common problems

## 🆘 Need Help?

- **Configuration Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Advanced Settings?** See [Advanced Configuration](../configuration/advanced.md)
- **General Questions?** Browse [FAQ](../support/faq.md)

---

## 🎯 Quick Reference

### **Essential Configuration**
```yaml
server:
  websocket: ws://YOUR_IP:8000/xiaozhi/v1/
  ota: http://YOUR_IP:8003/xiaozhi/ota/

selected_module:
  ASR: WhisperASR
  LLM: LMStudioLLM
  TTS: EdgeTTS
```

### **AI Provider Keys**
- **OpenAI**: `api_key: your-openai-api-key`
- **LMStudio**: `base_url: http://localhost:1234/v1`
- **EdgeTTS**: No API key required

### **Common Settings**
- **Port**: 8000 (WebSocket), 8003 (OTA)
- **Sample Rate**: 16000 Hz
- **Audio Format**: WAV, 16-bit, mono
- **Memory**: 20 messages, 24 hours

---

**Your configuration reference is ready! 🎉**

👉 **[Next: Communication Protocols →](protocols.md)**
