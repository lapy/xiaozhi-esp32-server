# Local Docker Image Compilation Method

This project now uses GitHub automatic Docker compilation functionality. This document is prepared for friends who need to compile Docker images locally.

## Prerequisites

1. Install Docker
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

2. Download ASR Models (Automatic)
The `docker-setup.sh` script automatically downloads required ASR models including:
- VOSK English model for offline speech recognition
- Sherpa ONNX models for multilingual ASR support

## Docker Image Compilation

1. Compile Docker images
```bash
# Enter project root directory
# Compile server
docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .

# Compile web
docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .
```

2. Start the project
```bash
# After compilation is complete, you can use docker-compose to start the project
# You need to modify docker-compose.yml to use your compiled image version
cd main/xiaozhi-server
docker-compose up -d
```

## ASR Model Configuration

The Docker setup includes automatic download of ASR models during the `docker-setup.sh` installation process. The following models are included:

### VOSK English Model
- **Model**: `vosk-model-en-us-0.22`
- **Languages**: English
- **Size**: ~50MB
- **Usage**: Offline English speech recognition

### Sherpa ONNX Models
- **Sherpa ONNX Sense Voice**: Multilingual support (Chinese, English, Japanese, Korean, Cantonese)
- **Sherpa ONNX Paraformer**: Lightweight Chinese ASR
- **Size**: ~300MB total
- **Usage**: High-accuracy multilingual speech recognition

### Configuration Example
```yaml
ASR:
  VoskASR:
    type: vosk
    model_path: models/vosk/vosk-model-en-us-0.22
    output_dir: tmp/
    
  SherpaASR:
    type: sherpa_onnx_local
    model_dir: models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17
    model_type: sense_voice
    output_dir: tmp/
    
  SherpaParaformerASR:
    type: sherpa_onnx_local
    model_dir: models/sherpa-onnx-paraformer-zh-small-2024-03-09
    model_type: paraformer
    output_dir: tmp/
```

## Volume Mounts

The Docker Compose configuration includes the following volume mounts for models:

```yaml
volumes:
  # Configuration file directory
  - ./data:/opt/xiaozhi-esp32-server/data
  # VOSK model mount
  - ./models/vosk:/opt/xiaozhi-esp32-server/models/vosk
  # Sherpa ONNX model mounts
  - ./models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17:/opt/xiaozhi-esp32-server/models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17
  - ./models/sherpa-onnx-paraformer-zh-small-2024-03-09:/opt/xiaozhi-esp32-server/models/sherpa-onnx-paraformer-zh-small-2024-03-09
```

## Automatic Model Download

The `docker-setup.sh` script handles all model downloads automatically:

### Features
- **Automatic Detection**: Checks for existing models before downloading
- **Progress Tracking**: Shows download progress with detailed feedback
- **Error Handling**: Graceful fallback with helpful error messages
- **Dependency Management**: Installs required tools if missing
- **Cleanup**: Removes archive files after successful extraction

### Usage
```bash
# Run the complete setup script (recommended)
sudo bash docker-setup.sh
# All ASR models will be downloaded automatically during setup
```

## Troubleshooting

### Model Download Issues
- Ensure you have sufficient disk space (~350MB for all models)
- Check internet connectivity for model downloads
- Verify Docker has access to the models directory
- Models are downloaded to `/opt/xiaozhi-server/models/` during setup

### Performance Considerations
- Models are downloaded during the setup process, not during Docker build
- This approach reduces Docker image size and build time
- Models are cached locally for faster subsequent deployments
- Consider using pre-built images from Docker Hub for faster deployment