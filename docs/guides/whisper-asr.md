# Whisper ASR Integration Guide

[TOC]

-----

## Introduction

OpenAI Whisper is a state-of-the-art automatic speech recognition (ASR) system that provides excellent accuracy for multilingual speech recognition. This guide will help you integrate and configure Whisper ASR with the Xiaozhi ESP32 Server.

## Features

- **Offline Operation**: Complete offline speech recognition after initial model download
- **Multilingual Support**: Supports 99+ languages with auto-detection
- **Multiple Model Sizes**: From tiny (39MB) to large-v3 (1.5GB) models
- **GPU Acceleration**: Automatic CUDA detection and usage
- **High Accuracy**: State-of-the-art accuracy for speech recognition

## Available Models

| Model | Size | Speed | Accuracy | Languages | Recommended Use |
|-------|------|-------|----------|-----------|-----------------|
| tiny.en | ~39 MB | Fastest | Lowest | English only | Real-time applications, limited resources |
| tiny | ~39 MB | Fastest | Lowest | Multilingual | Real-time applications, limited resources |
| base.en | ~74 MB | Fast | Good | English only | Balanced performance for English |
| base | ~74 MB | Fast | Good | Multilingual | **Recommended default** |
| small.en | ~244 MB | Medium | Better | English only | Better accuracy for English |
| small | ~244 MB | Medium | Better | Multilingual | Better accuracy, multilingual |
| medium.en | ~769 MB | Slow | High | English only | High accuracy for English |
| medium | ~769 MB | Slow | High | Multilingual | High accuracy, multilingual |
| large-v1 | ~1550 MB | Slowest | Highest | Multilingual | Maximum accuracy |
| large-v2 | ~1550 MB | Slowest | Highest | Multilingual | Maximum accuracy |
| large-v3 | ~1550 MB | Slowest | Highest | Multilingual | **Latest model, maximum accuracy** |

## Installation and Setup

### Method 1: Automatic Setup (Recommended)

The Whisper models are automatically downloaded when first used. The `docker-setup.sh` script creates the necessary directories and download scripts.

```bash
# Run the setup script (if not already done)
./docker-setup.sh
```

### Method 2: Manual Model Download

If you want to pre-download models or download them manually:

```bash
# Navigate to the Whisper models directory
cd /opt/xiaozhi-server/models/whisper

# Download a specific model
python3 download_models.py --model base --dir /opt/xiaozhi-server/models/whisper

# Download all models (takes a long time and requires significant disk space)
./download_all_models.sh
```

## Configuration

### Basic Configuration

Add the following to your `config.yaml` file:

```yaml
selected_module:
  ASR: WhisperASR

ASR:
  WhisperASR:
    type: whisper
    model_name: base  # Choose from available models above
    device: auto      # auto (auto-detect), cpu, cuda (GPU acceleration)
    language: null    # null for auto-detect, or specific language code
    output_dir: tmp/
```

### Advanced Configuration Options

```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: large-v3        # Use the latest and most accurate model
    device: cuda                # Force GPU usage (requires CUDA)
    language: "en"              # Force English recognition
    output_dir: tmp/
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | `whisper` | Provider type (must be "whisper") |
| `model_name` | string | `base` | Whisper model to use |
| `device` | string | `auto` | Device selection: `auto`, `cpu`, `cuda` |
| `language` | string/null | `null` | Language code or `null` for auto-detect |
| `output_dir` | string | `tmp/` | Directory for temporary audio files |

### Supported Language Codes

Whisper supports 99+ languages. Common language codes include:

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | `en` | Japanese | `ja` |
| French | `fr` | Korean | `ko` |
| German | `de` | Russian | `ru` |
| Italian | `it` | Arabic | `ar` |
| Portuguese | `pt` | Hindi | `hi` |

For the complete list, refer to the [Whisper documentation](https://github.com/openai/whisper#available-models-and-languages).

## Performance Optimization

### Model Selection Guidelines

1. **For Real-time Applications**: Use `tiny` or `base` models
2. **For Balanced Performance**: Use `base` or `small` models
3. **For Maximum Accuracy**: Use `large-v3` model
4. **For English Only**: Use `.en` variants for better performance

### Device Configuration

```yaml
# For systems with GPU
device: cuda

# For CPU-only systems
device: cpu

# For automatic detection (recommended)
device: auto
```

### Language Optimization

```yaml
# For auto-detection (recommended for multilingual environments)
language: null

# For specific language (faster processing)
language: "en"
```

## Usage Examples

### Example 1: English-Only Setup

```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base.en
    device: auto
    language: "en"
    output_dir: tmp/
```

### Example 2: Multilingual Setup

```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: null  # Auto-detect language
    output_dir: tmp/
```

### Example 3: High-Accuracy Setup

```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: large-v3
    device: cuda
    language: null
    output_dir: tmp/
```

## Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solution**: Use a smaller model or switch to CPU:
```yaml
model_name: base  # Instead of large-v3
device: cpu       # Force CPU usage
```

#### 2. Model Download Fails

**Error**: Models not downloading automatically

**Solution**: Download manually:
```bash
cd /opt/xiaozhi-server/models/whisper
python3 download_models.py --model base --dir /opt/xiaozhi-server/models/whisper
```

#### 3. Slow Processing

**Issue**: Speech recognition is too slow

**Solutions**:
- Use a smaller model (`tiny`, `base`)
- Use language-specific models (`.en` variants)
- Specify the language instead of auto-detection

#### 4. Low Accuracy

**Issue**: Recognition accuracy is poor

**Solutions**:
- Use a larger model (`small`, `medium`, `large-v3`)
- Ensure clear audio input
- Use language-specific models when possible

### Performance Monitoring

Monitor Whisper performance through logs:

```bash
# Check Whisper logs
docker logs xiaozhi-server | grep -i whisper

# Monitor processing times
docker logs xiaozhi-server | grep "Whisper transcription completed"
```

## Comparison with Other ASR Providers

| Provider | Type | Accuracy | Speed | Languages | Offline |
|----------|------|----------|-------|-----------|---------|
| Whisper | Local | Very High | Medium | 99+ | ✅ |
| OpenAI ASR | API | High | Fast | 99+ | ❌ |
| Vosk | Local | Medium | Fast | 20+ | ✅ |
| Sherpa ONNX | Local | High | Fast | 10+ | ✅ |
| Gemini ASR | API | High | Fast | 99+ | ❌ |

## Best Practices

1. **Start with `base` model**: Good balance of speed and accuracy
2. **Use GPU when available**: Significantly faster processing
3. **Specify language when known**: Improves accuracy and speed
4. **Monitor disk space**: Large models require significant storage
5. **Test different models**: Find the best fit for your use case

## Additional Resources

- [Whisper GitHub Repository](https://github.com/openai/whisper)
- [Whisper Paper](https://arxiv.org/abs/2212.04356)
- [Xiaozhi ESP32 Server Documentation](../README.md)
- [Performance Testing Guide](../guides/dev-ops.md)

## Support

For issues related to Whisper ASR integration:

1. Check the troubleshooting section above
2. Review the application logs
3. Test with different model configurations
4. Open an issue on the project repository

---

*Last updated: January 2025*
