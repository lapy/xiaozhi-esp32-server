# ⚙️ Configuration Examples

This guide provides real-world configuration examples for different use cases and scenarios.

## 🎯 Configuration Examples Overview

These examples cover:
- **Home Assistant** integration setups
- **Educational** and learning environments
- **Professional** deployment configurations
- **Development** and testing setups
- **High-performance** configurations

## 🏠 Home Assistant Integration

### **Complete Smart Home Setup**

```yaml
# Complete Home Assistant integration
server:
  websocket: ws://192.168.1.100:8000/xiaozhi/v1/
  ota: http://192.168.1.100:8003/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: WhisperASR
  LLM: LMStudioLLM
  TTS: EdgeTTS

# AI Configuration
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: en
    output_dir: tmp/

LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    temperature: 0.7
    max_tokens: 1000
    timeout: 30

TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural
    rate: 1.0
    volume: 1.0
    output_dir: tmp/

# Home Assistant Integration
homeassistant:
  enabled: true
  url: http://homeassistant.local:8123
  api_key: your-homeassistant-api-key
  entities:
    lights:
      - light.living_room
      - light.kitchen
      - light.bedroom
    switches:
      - switch.coffee_maker
      - switch.tv_power
    sensors:
      - sensor.temperature
      - sensor.humidity
    climate:
      - climate.thermostat

# Function Calling for Smart Home
function_calling:
  enabled: true
  functions:
    - name: control_light
      description: Control smart home lights
      parameters:
        entity_id:
          type: string
          description: HomeAssistant entity ID
          required: true
        action:
          type: string
          enum: [on, off, toggle, dim]
          required: true
        brightness:
          type: integer
          description: Brightness level (0-255)
          required: false
    
    - name: get_weather
      description: Get current weather information
      parameters:
        location:
          type: string
          description: City name
          required: true
    
    - name: set_temperature
      description: Set thermostat temperature
      parameters:
        temperature:
          type: number
          description: Temperature in Celsius
          required: true

# Memory for context
memory:
  mem_local_short:
    type: local_short
    max_messages: 30
    max_age_hours: 24

# Voice Activity Detection
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 800
    pre_padding_ms: 300
    post_padding_ms: 300
```

### **Voice Commands for Smart Home**

```yaml
# Custom voice commands
voice_commands:
  enabled: true
  
  commands:
    - pattern: "turn on the (.*) light"
      function: control_light
      parameters:
        entity_id: "light.{1}"
        action: "on"
    
    - pattern: "turn off the (.*) light"
      function: control_light
      parameters:
        entity_id: "light.{1}"
        action: "off"
    
    - pattern: "dim the (.*) light to (.*) percent"
      function: control_light
      parameters:
        entity_id: "light.{1}"
        action: "dim"
        brightness: "{2}"
    
    - pattern: "set temperature to (.*) degrees"
      function: set_temperature
      parameters:
        temperature: "{1}"
    
    - pattern: "what's the weather like"
      function: get_weather
      parameters:
        location: "current"
```

## 🎓 Educational Environment

### **Classroom Learning Setup**

```yaml
# Educational configuration for classroom use
server:
  websocket: ws://192.168.1.50:8000/xiaozhi/v1/
  ota: http://192.168.1.50:8003/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: WhisperASR
  LLM: OpenAILLM
  TTS: EdgeTTS

# Educational AI Configuration
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: en
    output_dir: tmp/

LLM:
  OpenAILLM:
    type: openai
    api_key: your-openai-api-key
    model: gpt-4o-mini
    temperature: 0.3          # Lower temperature for more consistent responses
    max_tokens: 500           # Shorter responses for educational context
    timeout: 30

TTS:
  EdgeTTS:
    type: edge
    voice: en-US-JennyNeural  # Friendly, educational voice
    rate: 0.9                 # Slightly slower for clarity
    volume: 1.0
    output_dir: tmp/

# Educational plugins
plugins:
  enabled: true
  
  # Math helper
  math_helper:
    enabled: true
    functions:
      - calculate
      - solve_equation
      - explain_concept
  
  # Language learning
  language_learning:
    enabled: true
    target_language: spanish
    difficulty: beginner
    functions:
      - translate
      - practice_conversation
      - grammar_check
  
  # Science assistant
  science_assistant:
    enabled: true
    subjects: [physics, chemistry, biology]
    functions:
      - explain_concept
      - solve_problem
      - provide_examples

# Educational memory settings
memory:
  mem_local_short:
    type: local_short
    max_messages: 50          # More context for learning
    max_age_hours: 48        # Longer memory for educational sessions

# Educational voice settings
VAD:
  SileroVAD:
    threshold: 0.4            # More sensitive for student questions
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 1000  # Longer pause for student thinking
    pre_padding_ms: 500
    post_padding_ms: 500

# Educational prompts
prompts:
  system: |
    You are an educational assistant designed to help students learn. 
    You should:
    - Provide clear, step-by-step explanations
    - Encourage critical thinking
    - Ask follow-up questions to check understanding
    - Use age-appropriate language
    - Be patient and supportive
    
    When students ask questions, break down complex topics into 
    manageable parts and provide examples.
  
  user: |
    I'm a student learning about {topic}. Can you help me understand 
    this concept and provide some examples?
```

## 🏢 Professional Deployment

### **Enterprise Configuration**

```yaml
# Professional enterprise setup
server:
  websocket: wss://xiaozhi.company.com/xiaozhi/v1/
  ota: https://xiaozhi.company.com/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: OpenAIASR
  LLM: OpenAILLM
  TTS: OpenAITTS

# Professional AI Configuration
ASR:
  OpenAIASR:
    type: openai
    api_key: your-openai-api-key
    model: whisper-1
    language: en
    temperature: 0.0
    timeout: 30

LLM:
  OpenAILLM:
    type: openai
    api_key: your-openai-api-key
    model: gpt-4o
    temperature: 0.7
    max_tokens: 2000
    timeout: 60

TTS:
  OpenAITTS:
    type: openai
    api_key: your-openai-api-key
    model: tts-1
    voice: alloy
    speed: 1.0
    output_dir: tmp/

# Security Configuration
security:
  api_auth:
    enabled: true
    api_key: your-secure-api-key
    header_name: X-API-Key
  
  rate_limit:
    enabled: true
    requests_per_minute: 100
    burst_size: 20
  
  cors:
    enabled: true
    allowed_origins:
      - "https://company.com"
      - "https://app.company.com"
    allowed_methods: [GET, POST, PUT, DELETE]
    allowed_headers: [Content-Type, Authorization, X-API-Key]

# SSL/TLS Configuration
ssl:
  enabled: true
  cert_file: /etc/ssl/certs/xiaozhi.crt
  key_file: /etc/ssl/private/xiaozhi.key
  verify_certificates: true

# Professional monitoring
monitoring:
  enabled: true
  
  metrics:
    response_time: true
    memory_usage: true
    cpu_usage: true
    error_rate: true
  
  health_checks:
    enabled: true
    interval: 30
    timeout: 10
  
  alerts:
    enabled: true
    email:
      smtp_server: smtp.company.com
      username: alerts@company.com
      recipients: [admin@company.com, devops@company.com]

# Professional logging
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  files:
    main: /var/log/xiaozhi/main.log
    error: /var/log/xiaozhi/error.log
    access: /var/log/xiaozhi/access.log
  
  rotation:
    max_size: 100MB
    backup_count: 10
    when: midnight

# Professional backup
backup:
  enabled: true
  
  schedule:
    daily: true
    time: "03:00"
    retention_days: 90
  
  locations:
    - type: s3
      bucket: company-xiaozhi-backups
      region: us-east-1
      access_key: your-s3-access-key
      secret_key: your-s3-secret-key
  
  content:
    config_files: true
    database: true
    logs: true
    audio_cache: false

# Professional memory
memory:
  mem_local_short:
    type: local_short
    max_messages: 100
    max_age_hours: 24
  
  mem_local_long:
    type: local_long
    storage_path: /var/lib/xiaozhi/memory/
    max_entries: 10000
    similarity_threshold: 0.8

# Professional VAD
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700
    pre_padding_ms: 300
    post_padding_ms: 300
```

## 🚀 High-Performance Configuration

### **Optimized for Speed**

```yaml
# High-performance configuration
server:
  websocket: ws://192.168.1.200:8000/xiaozhi/v1/
  ota: http://192.168.1.200:8003/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: WhisperASR
  LLM: LMStudioLLM
  TTS: EdgeTTS

# High-performance AI Configuration
ASR:
  WhisperASR:
    type: whisper
    model_name: tiny           # Fastest model
    device: cuda              # GPU acceleration
    compute_type: float16     # Half precision
    language: en
    output_dir: tmp/
    streaming: true
    chunk_length: 10          # Smaller chunks for faster processing

LLM:
  LMStudioLLM:
    type: lmstudio
    base_url: http://localhost:1234/v1
    model_name: llama-3.1:8b
    temperature: 0.7
    max_tokens: 500           # Shorter responses for speed
    timeout: 15               # Shorter timeout
    streaming: true
    gpu_layers: 35            # Maximum GPU offload
    context_length: 2048     # Smaller context for speed

TTS:
  EdgeTTS:
    type: edge
    voice: en-US-AriaNeural
    rate: 1.2                 # Faster speech
    volume: 1.0
    output_dir: tmp/
    streaming: true

# Performance optimizations
performance:
  streaming: true
  caching: true
  gpu_acceleration: true
  model_optimization: true
  
  # Model caching
  model_cache:
    enabled: true
    cache_dir: models/cache/
    max_cache_size: 2000     # MB
    cleanup_interval: 1800   # 30 minutes
  
  # Audio processing optimization
  audio:
    sample_rate: 16000
    channels: 1
    bit_depth: 16
    buffer_size: 2048         # Smaller buffer for lower latency
    chunk_size: 512           # Smaller chunks

# Optimized VAD
VAD:
  SileroVAD:
    threshold: 0.6            # Higher threshold for faster detection
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 500  # Shorter silence detection
    pre_padding_ms: 200
    post_padding_ms: 200
    window_size: 256          # Smaller window
    hop_length: 128           # Smaller hop

# Optimized memory
memory:
  mem_local_short:
    type: local_short
    max_messages: 10          # Fewer messages for speed
    max_age_hours: 12          # Shorter memory
    cleanup_interval: 1800     # More frequent cleanup

# Performance monitoring
monitoring:
  enabled: true
  
  metrics:
    response_time: true
    memory_usage: true
    cpu_usage: true
    gpu_usage: true
    audio_processing_time: true
    model_inference_time: true
  
  # Real-time monitoring
  real_time:
    enabled: true
    update_interval: 1        # 1 second updates
    metrics_endpoint: /metrics
```

## 🧪 Development and Testing

### **Development Environment**

```yaml
# Development configuration
environment: development

server:
  websocket: ws://localhost:8000/xiaozhi/v1/
  ota: http://localhost:8003/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: MockASR
  LLM: MockLLM
  TTS: MockTTS

# Development AI Configuration (Mock services)
ASR:
  MockASR:
    type: mock
    response_delay: 0.5
    responses:
      - "Hello world"
      - "This is a test"
      - "Mock speech recognition"

LLM:
  MockLLM:
    type: mock
    response: "This is a mock response for development testing"
    response_delay: 1.0

TTS:
  MockTTS:
    type: mock
    response_delay: 0.5
    output_file: tmp/mock_audio.wav

# Development settings
development:
  debug: true
  hot_reload: true
  mock_ai_services: true
  reduced_logging: false
  
  # Development plugins
  plugins:
    enabled: true
    
    # Test plugin
    test_plugin:
      enabled: true
      functions:
        - test_function
        - mock_integration
  
  # Development memory
  memory:
    mem_local_short:
      type: local_short
      max_messages: 5
      max_age_hours: 1

# Development logging
logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  files:
    main: logs/dev.log
    error: logs/dev_error.log
  
  # Console logging for development
  console:
    enabled: true
    level: DEBUG

# Development VAD
VAD:
  SileroVAD:
    threshold: 0.3            # More sensitive for testing
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 500
    pre_padding_ms: 200
    post_padding_ms: 200
```

### **Testing Configuration**

```yaml
# Testing configuration
environment: testing

server:
  websocket: ws://test-server:8000/xiaozhi/v1/
  ota: http://test-server:8003/xiaozhi/ota/

selected_module:
  VAD: SileroVAD
  ASR: TestASR
  LLM: TestLLM
  TTS: TestTTS

# Testing AI Configuration
ASR:
  TestASR:
    type: test
    test_cases:
      - input: "test_audio_1.wav"
        output: "Hello, this is a test"
      - input: "test_audio_2.wav"
        output: "Testing speech recognition"

LLM:
  TestLLM:
    type: test
    test_responses:
      - input: "Hello"
        output: "Hi there! How can I help you?"
      - input: "What's the weather?"
        output: "I can help you check the weather. What location?"

TTS:
  TestTTS:
    type: test
    output_dir: test_output/
    test_files: true

# Testing settings
testing:
  enabled: true
  
  # Test data
  test_data:
    audio_samples: test_data/audio/
    expected_responses: test_data/responses/
    test_configs: test_data/configs/
  
  # Test execution
  execution:
    parallel_tests: true
    test_timeout: 30
    retry_failed: true
    max_retries: 3
  
  # Test reporting
  reporting:
    enabled: true
    format: json
    output_dir: test_reports/
    include_metrics: true

# Testing memory
memory:
  mem_local_short:
    type: local_short
    max_messages: 3
    max_age_hours: 1

# Testing VAD
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700
    pre_padding_ms: 300
    post_padding_ms: 300
```

## 🎯 Configuration Best Practices

### **General Best Practices**

1. **Start Simple**: Begin with basic configuration and add complexity gradually
2. **Test Incrementally**: Test each component after configuration changes
3. **Monitor Performance**: Use monitoring to identify bottlenecks
4. **Backup Configurations**: Keep backups of working configurations
5. **Document Changes**: Document any custom modifications

### **Security Best Practices**

1. **Use Environment Variables**: Store sensitive data in environment variables
2. **Enable Authentication**: Always enable API authentication in production
3. **Use HTTPS/WSS**: Use secure connections for production deployments
4. **Regular Updates**: Keep all components updated
5. **Access Control**: Implement proper access controls

### **Performance Best Practices**

1. **Choose Appropriate Models**: Select models based on your performance requirements
2. **Enable Caching**: Use caching for frequently accessed data
3. **Optimize Audio Settings**: Tune audio parameters for your use case
4. **Monitor Resources**: Keep an eye on CPU, memory, and GPU usage
5. **Load Testing**: Test your configuration under expected load

## 🆘 Troubleshooting Configuration Issues

### **Common Issues and Solutions**

#### **Configuration Validation Errors**
```bash
# Validate configuration
python -m xiaozhi.config_validator --config data/.config.yaml
```

#### **Performance Issues**
```yaml
# Enable performance monitoring
monitoring:
  enabled: true
  metrics:
    response_time: true
    memory_usage: true
    cpu_usage: true
```

#### **Memory Issues**
```yaml
# Optimize memory usage
memory:
  mem_local_short:
    max_messages: 10          # Reduce message count
    max_age_hours: 12         # Reduce memory age
```

## 🎯 Next Steps

After reviewing these examples:

1. **[Basic Setup](basic-setup.md)** - Start with basic configuration
2. **[Advanced Configuration](advanced.md)** - Add advanced features
3. **[Provider Configuration](providers.md)** - Configure specific providers
4. **[Testing Your Setup](../getting-started/first-device.md)** - Verify everything works

## 🆘 Need Help?

- **Configuration Questions?** Check [Basic Setup](basic-setup.md)
- **Performance Issues?** See [Advanced Configuration](advanced.md)
- **Provider Setup?** Review [Provider Configuration](providers.md)

---

## 🎯 Quick Reference

### **Configuration Templates**
- **Home Assistant**: Complete smart home integration
- **Educational**: Classroom learning environment
- **Professional**: Enterprise deployment
- **High-Performance**: Optimized for speed
- **Development**: Testing and development

### **Key Settings**
- **ASR**: WhisperASR (offline) or OpenAIASR (cloud)
- **LLM**: LMStudioLLM (local) or OpenAILLM (cloud)
- **TTS**: EdgeTTS (free) or OpenAITTS (premium)

---

**Your configuration examples are ready! 🎉**

👉 **[Next: Provider Configuration →](providers.md)**
