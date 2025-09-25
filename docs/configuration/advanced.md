# ⚙️ Advanced Configuration

This guide covers advanced configuration options for fine-tuning Xiaozhi ESP32 Server performance, security, and functionality.

## 🎯 Advanced Configuration Overview

Advanced configuration allows you to:
- **Optimize performance** for your specific use case
- **Configure security** settings and authentication
- **Set up custom plugins** and integrations
- **Fine-tune AI models** and parameters
- **Configure logging** and monitoring

## 🔧 Performance Optimization

### **Streaming Configuration**

Enable streaming for faster response times:

```yaml
# Enable streaming for all components
streaming:
  enabled: true
  buffer_size: 1024
  chunk_size: 512

# Component-specific streaming
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    streaming: true
    chunk_length: 30        # Process audio in 30-second chunks
    overlap: 2               # 2-second overlap between chunks

LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    streaming: true
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
```

### **Model Optimization**

#### **GPU Acceleration**
```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: cuda              # Use GPU acceleration
    compute_type: float16    # Use half precision for speed
    batch_size: 4            # Process multiple audio chunks

LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    gpu_layers: 35           # Number of layers to offload to GPU
    context_length: 4096     # Context window size
```

#### **Model Caching**
```yaml
# Enable model caching for faster startup
model_cache:
  enabled: true
  cache_dir: models/cache/
  max_cache_size: 5000      # MB
  cleanup_interval: 3600    # seconds
```

### **Audio Processing Optimization**

```yaml
# Audio processing settings
audio:
  sample_rate: 16000        # Standard sample rate
  channels: 1               # Mono audio
  bit_depth: 16             # 16-bit audio
  buffer_size: 4096         # Audio buffer size
  chunk_size: 1024          # Processing chunk size

# VAD optimization
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700
    pre_padding_ms: 300
    post_padding_ms: 300
    # Advanced VAD settings
    window_size: 512
    hop_length: 256
    min_speech_duration_ms: 250
    max_speech_duration_ms: 30000
```

## 🔐 Security Configuration

### **API Authentication**

```yaml
# API security settings
security:
  # Enable API key authentication
  api_auth:
    enabled: true
    api_key: your-secure-api-key-here
    header_name: X-API-Key
  
  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60
    burst_size: 10
  
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

### **WebSocket Security**

```yaml
# WebSocket security
websocket:
  # Enable SSL/TLS
  ssl:
    enabled: true
    cert_file: /path/to/cert.pem
    key_file: /path/to/key.pem
  
  # Authentication
  auth:
    enabled: true
    token_expiry: 3600       # 1 hour
    refresh_token_expiry: 86400  # 24 hours
  
  # Connection limits
  max_connections: 100
  max_connections_per_ip: 10
  connection_timeout: 300    # 5 minutes
```

### **Data Encryption**

```yaml
# Data encryption settings
encryption:
  # Encrypt stored data
  storage:
    enabled: true
    algorithm: AES-256-GCM
    key_file: /path/to/encryption.key
  
  # Encrypt audio data
  audio:
    enabled: true
    algorithm: AES-128-CBC
    key_rotation: 86400      # Rotate keys daily
```

## 🔌 Plugin Configuration

### **Custom Plugin Development**

```yaml
# Plugin system configuration
plugins:
  enabled: true
  plugin_dir: plugins/
  auto_load: true
  
  # Plugin-specific settings
  weather:
    api_key: your-weather-api-key
    units: metric
    cache_duration: 300
  
  news:
    api_key: your-news-api-key
    sources: ["bbc", "cnn", "reuters"]
    max_articles: 10
  
  smart_home:
    homeassistant_url: http://homeassistant.local:8123
    api_key: your-ha-api-key
    entities:
      - light.living_room
      - switch.kitchen
      - sensor.temperature
```

### **Function Calling Configuration**

```yaml
# Function calling settings
function_calling:
  enabled: true
  
  # Available functions
  functions:
    - name: get_weather
      description: Get current weather information
      parameters:
        location:
          type: string
          description: City name or coordinates
          required: true
    
    - name: control_light
      description: Control smart home lights
      parameters:
        entity_id:
          type: string
          description: HomeAssistant entity ID
          required: true
        action:
          type: string
          enum: [on, off, toggle]
          required: true
```

## 📊 Monitoring and Logging

### **Logging Configuration**

```yaml
# Logging settings
logging:
  level: INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL
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
```

### **Performance Monitoring**

```yaml
# Performance monitoring
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
    interval: 30             # seconds
    timeout: 10              # seconds
    
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

### **Alerting Configuration**

```yaml
# Alerting settings
alerts:
  enabled: true
  
  # Email alerts
  email:
    smtp_server: smtp.gmail.com
    smtp_port: 587
    username: your-email@gmail.com
    password: your-app-password
    recipients:
      - admin@yourdomain.com
  
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
      threshold: 5.0        # seconds
      operator: greater_than
    
    - name: low_memory
      metric: memory_usage
      threshold: 90           # percentage
      operator: greater_than
```

## 🌐 Network Configuration

### **Proxy Settings**

```yaml
# Network proxy configuration
network:
  # HTTP proxy
  http_proxy:
    enabled: true
    host: proxy.company.com
    port: 8080
    username: proxy_user
    password: proxy_password
  
  # HTTPS proxy
  https_proxy:
    enabled: true
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
# Load balancing configuration
load_balancer:
  enabled: true
  
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

## 🔄 Backup and Recovery

### **Configuration Backup**

```yaml
# Backup configuration
backup:
  enabled: true
  
  # Backup schedule
  schedule:
    daily: true
    time: "02:00"           # 2 AM
    retention_days: 30
  
  # Backup locations
  locations:
    - type: local
      path: /backups/xiaozhi/
    
    - type: s3
      bucket: xiaozhi-backups
      region: us-west-2
      access_key: your-access-key
      secret_key: your-secret-key
  
  # Backup content
  content:
    config_files: true
    model_files: true
    database: true
    logs: true
    audio_cache: false       # Skip large audio files
```

### **Disaster Recovery**

```yaml
# Disaster recovery settings
disaster_recovery:
  enabled: true
  
  # Recovery procedures
  procedures:
    - name: full_restore
      description: Complete system restore
      steps:
        - restore_config
        - restore_database
        - restore_models
        - restart_services
    
    - name: config_only
      description: Restore configuration only
      steps:
        - restore_config
        - restart_services
  
  # Recovery testing
  testing:
    enabled: true
    schedule: weekly
    test_restore: true
```

## 🎯 Environment-Specific Configuration

### **Development Environment**

```yaml
# Development settings
environment: development

# Development-specific overrides
development:
  debug: true
  hot_reload: true
  mock_ai_services: true
  reduced_logging: false
  
  # Development AI providers
  ASR:
    MockASR:
      type: mock
      response_delay: 0.5
  
  LLM:
    MockLLM:
      type: mock
      response: "This is a mock response for development"
```

### **Production Environment**

```yaml
# Production settings
environment: production

# Production-specific overrides
production:
  debug: false
  hot_reload: false
  mock_ai_services: false
  reduced_logging: true
  
  # Production optimizations
  performance:
    enable_caching: true
    enable_compression: true
    enable_monitoring: true
  
  # Security hardening
  security:
    strict_cors: true
    rate_limiting: true
    input_validation: true
```

## 🛠️ Troubleshooting Advanced Issues

### **Performance Issues**

#### **Slow Response Times**
```yaml
# Optimize for speed
performance:
  streaming: true
  caching: true
  gpu_acceleration: true
  model_optimization: true
```

#### **High Memory Usage**
```yaml
# Optimize memory usage
memory:
  model_cache_size: 1000    # MB
  audio_buffer_size: 2048   # samples
  max_concurrent_requests: 5
```

### **Security Issues**

#### **Authentication Failures**
```yaml
# Debug authentication
security:
  debug_auth: true
  log_auth_attempts: true
  auth_timeout: 30
```

#### **SSL/TLS Issues**
```yaml
# SSL debugging
ssl:
  debug: true
  verify_certificates: true
  cipher_suites: ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"]
```

## 🎯 Next Steps

After advanced configuration:

1. **[Configuration Examples](examples.md)** - Real-world configuration examples
2. **[Performance Tuning](../guides/performance.md)** - Optimize for your use case
3. **[Security Hardening](../guides/security.md)** - Secure your deployment
4. **[Monitoring Setup](../guides/monitoring.md)** - Set up comprehensive monitoring

## 🆘 Need Help?

- **Configuration Issues?** Check [Troubleshooting](../support/troubleshooting.md)
- **Performance Questions?** See [Performance Guide](../guides/performance.md)
- **Security Concerns?** Review [Security Guide](../guides/security.md)

---

## 🎯 Quick Reference

### **Performance Optimization**
```yaml
streaming: true
gpu_acceleration: true
model_caching: true
```

### **Security Essentials**
```yaml
api_auth: true
ssl_enabled: true
rate_limiting: true
```

### **Monitoring Setup**
```yaml
logging: INFO
metrics: true
health_checks: true
```

---

**Your advanced configuration is ready! 🎉**

👉 **[Next: Configuration Examples →](examples.md)**
