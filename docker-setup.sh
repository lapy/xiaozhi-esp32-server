#!/bin/sh
# Script author @VanillaNahida
# This file is used for one-click automatic download of required files for this project and automatic directory creation
# Currently only supports X86 version of Ubuntu system, other systems are not tested

# Define interrupt handler function
handle_interrupt() {
    echo ""
    echo "Installation interrupted by user (Ctrl+C or Esc)"
    echo "To reinstall, please run the script again"
    exit 1
}

# Set signal capture to handle Ctrl+C
trap handle_interrupt SIGINT

# Handle Esc key
# Save terminal settings
old_stty_settings=$(stty -g)
# Set terminal to respond immediately, no echo
stty -icanon -echo min 1 time 0

# Background process to detect Esc key
(while true; do
    read -r key
    if [[ $key == $'\e' ]]; then
        # Detected Esc key, trigger interrupt handler
        kill -SIGINT $$
        break
    fi
done) &

# Restore terminal settings when script ends


# Print colored ASCII art
echo -e "\e[1;32m"  # Set color to bright green
cat << "EOF"
Script Author: @Bilibili Vanilla Nahida Meow
 __      __            _  _  _            _   _         _      _      _        
 \ \    / /           (_)| || |          | \ | |       | |    (_)    | |       
  \ \  / /__ _  _ __   _ | || |  __ _    |  \| |  __ _ | |__   _   __| |  __ _ 
   \ \/ // _` || '_ \ | || || | / _` |   | . ` | / _` || '_ \ | | / _` | / _` |
    \  /| (_| || | | || || || || (_| |   | |\  || (_| || | | || || (_| || (_| |
     \/  \__,_||_| |_||_||_||_| \__,_|   |_| \_| \__,_||_| |_||_| \__,_| \__,_|                                                                                                                                                                                                                               
EOF
echo -e "\e[0m"  # Reset color
echo -e "\e[1;36m  Xiaozhi Server Full Deployment One-Click Installation Script Ver 0.2 Updated August 20, 2025 \e[0m\n"
sleep 1



# Check and install whiptail
check_whiptail() {
    if ! command -v whiptail &> /dev/null; then
        echo "Installing whiptail..."
        apt update
        apt install -y whiptail
    fi
}

check_whiptail

# Create confirmation dialog
whiptail --title "Installation Confirmation" --yesno "About to install Xiaozhi Server, continue?" \
  --yes-button "Continue" --no-button "Exit" 10 50

# Execute operation based on user choice
case $? in
  0)
    ;;
  1)
    exit 1
    ;;
esac

# Check root permissions
if [ $EUID -ne 0 ]; then
    whiptail --title "Permission Error" --msgbox "Please run this script with root privileges" 10 50
    exit 1
fi

# Check system version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "debian" ] && [ "$ID" != "ubuntu" ]; then
        whiptail --title "System Error" --msgbox "This script only supports Debian/Ubuntu systems" 10 60
        exit 1
    fi
else
    whiptail --title "System Error" --msgbox "Cannot determine system version, this script only supports Debian/Ubuntu systems" 10 60
    exit 1
fi

# Download configuration file function
check_and_download() {
    local filepath=$1
    local url=$2
    if [ ! -f "$filepath" ]; then
        if ! curl -fL --progress-bar "$url" -o "$filepath"; then
            whiptail --title "Error" --msgbox "${filepath} file download failed" 10 50
            exit 1
        fi
    else
        echo "${filepath} file already exists, skipping download"
    fi
}

# Check if already installed
check_installed() {
    # Check if directory exists and is not empty
    if [ -d "/opt/xiaozhi-server/" ] && [ "$(ls -A /opt/xiaozhi-server/)" ]; then
        DIR_CHECK=1
    else
        DIR_CHECK=0
    fi
    
    # Check if container exists
    if docker inspect xiaozhi-esp32-server > /dev/null 2>&1; then
        CONTAINER_CHECK=1
    else
        CONTAINER_CHECK=0
    fi
    
    # Both checks passed
    if [ $DIR_CHECK -eq 1 ] && [ $CONTAINER_CHECK -eq 1 ]; then
        return 0  # Already installed
    else
        return 1  # Not installed
    fi
}

# Update related
if check_installed; then
    if whiptail --title "Installation Detected" --yesno "Xiaozhi server installation detected, do you want to upgrade?" 10 60; then
        # User chose to upgrade, execute cleanup operations
        echo "Starting upgrade operation..."
        
        # Stop and remove all docker-compose services
        docker compose -f /opt/xiaozhi-server/docker-compose_all.yml down
        
        # Stop and delete specific containers (considering containers may not exist)
        containers=(
            "xiaozhi-esp32-server"
            "xiaozhi-esp32-server-web"
            "xiaozhi-esp32-server-db"
            "xiaozhi-esp32-server-redis"
        )
        
        for container in "${containers[@]}"; do
            if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
                docker stop "$container" >/dev/null 2>&1 && \
                docker rm "$container" >/dev/null 2>&1 && \
                echo "Successfully removed container: $container"
            else
                echo "Container does not exist, skipping: $container"
            fi
        done
        
        # Delete specific images (considering images may not exist)
        images=(
            "ghcr.io/lapy/xiaozhi-esp32-server:server_latest"
            "ghcr.io/lapy/xiaozhi-esp32-server:web_latest"
        )
        
        for image in "${images[@]}"; do
            if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${image}$"; then
                docker rmi "$image" >/dev/null 2>&1 && \
                echo "Successfully deleted image: $image"
            else
                echo "Image does not exist, skipping: $image"
            fi
        done
        
        echo "All cleanup operations completed"
        
        # Backup original configuration files
        mkdir -p /opt/xiaozhi-server/backup/
        if [ -f /opt/xiaozhi-server/data/.config.yaml ]; then
            cp /opt/xiaozhi-server/data/.config.yaml /opt/xiaozhi-server/backup/.config.yaml
            echo "Original configuration file backed up to /opt/xiaozhi-server/backup/.config.yaml"
        fi
        
        # Download latest configuration files
        check_and_download "/opt/xiaozhi-server/docker-compose_all.yml" "https://raw.githubusercontent.com/lapy/xiaozhi-esp32-server/main/main/xiaozhi-server/docker-compose_all.yml"
        check_and_download "/opt/xiaozhi-server/data/.config.yaml" "https://raw.githubusercontent.com/lapy/xiaozhi-esp32-server/main/main/xiaozhi-server/config_from_api.yaml"
        
        # Start Docker services
        echo "Starting latest version services..."
        # Mark upgrade completion, skip subsequent download steps
        UPGRADE_COMPLETED=1
        docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d
    else
          whiptail --title "Skip Upgrade" --msgbox "Upgrade cancelled, will continue using current version." 10 50
          # Skip upgrade, continue with subsequent installation process
    fi
fi


# Check curl installation
if ! command -v curl &> /dev/null; then
    echo "------------------------------------------------------------"
    echo "curl not detected, installing..."
    apt update
    apt install -y curl
else
    echo "------------------------------------------------------------"
    echo "curl already installed, skipping installation step"
fi

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "------------------------------------------------------------"
    echo "Docker not detected, installing..."
    
    # Use official Docker source
    DISTRO=$(lsb_release -cs)
    MIRROR_URL="https://download.docker.com/linux/ubuntu"
    GPG_URL="https://download.docker.com/linux/ubuntu/gpg"
    
    # Install basic dependencies
    apt update
    apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg
    
    # Create key directory and add domestic mirror source key
    mkdir -p /etc/apt/keyrings
    curl -fsSL "$GPG_URL" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Add domestic mirror source
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] $MIRROR_URL $DISTRO stable" \
        > /etc/apt/sources.list.d/docker.list
    
    # Add backup official source key (avoid domestic source key verification failure)
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 2>/dev/null || \
    echo "Warning: Some keys failed to add, continuing installation attempt..."
    
    # Install Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    
    # Start services
    systemctl start docker
    systemctl enable docker
    
    # Check if installation was successful
    if docker --version; then
        echo "------------------------------------------------------------"
        echo "Docker installation completed!"
    else
        whiptail --title "Error" --msgbox "Docker installation failed, please check logs." 10 50
        exit 1
    fi
else
    echo "Docker already installed, skipping installation step"
fi

# Docker mirror source configuration
MIRROR_OPTIONS=(
    "1" "Docker Hub Official (Recommended)"
    "2" "Google Container Registry"
    "3" "Amazon ECR Public"
    "4" "Microsoft Container Registry"
    "5" "Quay.io Registry"
    "6" "GitHub Container Registry"
    "7" "Custom Mirror Source"
    "8" "Skip Configuration"
)

MIRROR_CHOICE=$(whiptail --title "Select Docker Mirror Source" --menu "Please select the Docker mirror source to use" 20 60 10 \
"${MIRROR_OPTIONS[@]}" 3>&1 1>&2 2>&3) || {
    echo "User cancelled selection, exiting script"
    exit 1
}

case $MIRROR_CHOICE in
    1) MIRROR_URL="https://registry-1.docker.io" ;; 
    2) MIRROR_URL="https://gcr.io" ;; 
    3) MIRROR_URL="https://public.ecr.aws" ;; 
    4) MIRROR_URL="https://mcr.microsoft.com" ;; 
    5) MIRROR_URL="https://quay.io" ;; 
    6) MIRROR_URL="https://ghcr.io" ;; 
    7) MIRROR_URL=$(whiptail --title "Custom Mirror Source" --inputbox "Please enter the complete mirror source URL:" 10 60 3>&1 1>&2 2>&3) ;; 
    8) MIRROR_URL="" ;; 
esac

if [ -n "$MIRROR_URL" ]; then
    mkdir -p /etc/docker
    if [ -f /etc/docker/daemon.json ]; then
        cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
    fi
    cat > /etc/docker/daemon.json <<EOF
{
    "dns": ["8.8.8.8", "114.114.114.114"],
    "registry-mirrors": ["$MIRROR_URL"]
}
EOF
    whiptail --title "Configuration Success" --msgbox "Successfully added mirror source: $MIRROR_URL\nPlease press Enter to restart Docker service and continue..." 12 60
    echo "------------------------------------------------------------"
    echo "Starting Docker service restart..."
    systemctl restart docker.service
fi

# Create installation directory
echo "------------------------------------------------------------"
echo "Starting to create installation directory..."
# Check and create data directory
if [ ! -d /opt/xiaozhi-server/data ]; then
    mkdir -p /opt/xiaozhi-server/data
    echo "Created data directory: /opt/xiaozhi-server/data"
else
    echo "Directory xiaozhi-server/data already exists, skipping creation"
fi

# Check and create models directory
if [ ! -d /opt/xiaozhi-server/models ]; then
    mkdir -p /opt/xiaozhi-server/models
    echo "Created models directory: /opt/xiaozhi-server/models"
else
    echo "Directory xiaozhi-server/models already exists, skipping creation"
fi

# Download and extract Vosk English model
download_vosk_model() {
    echo "------------------------------------------------------------"
    echo "Checking Vosk English model..."
    
    VOSK_MODEL_DIR="/opt/xiaozhi-server/models/vosk"
    VOSK_MODEL_PATH="$VOSK_MODEL_DIR/vosk-model-en-us-0.22"
    
    # Check if model is already downloaded and extracted
    if [ -d "$VOSK_MODEL_PATH" ] && [ -f "$VOSK_MODEL_PATH/am/final.mdl" ]; then
        echo "Vosk English model already exists, skipping download"
        return 0
    fi
    
    echo "Vosk English model not found, starting download..."
    
    # Create vosk directory
    mkdir -p "$VOSK_MODEL_DIR"
    
    # Download the model
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    MODEL_ZIP="$VOSK_MODEL_DIR/vosk-model-en-us-0.22.zip"
    
    echo "Downloading Vosk English model from $MODEL_URL"
    echo "This may take several minutes depending on your internet connection..."
    
    if ! curl -L --progress-bar "$MODEL_URL" -o "$MODEL_ZIP"; then
        echo "Warning: Failed to download Vosk model. You can download it manually later."
        echo "Visit: https://alphacephei.com/vosk/models"
        echo "Download: vosk-model-en-us-0.22.zip"
        echo "Extract to: $VOSK_MODEL_DIR/"
        return 1
    fi
    
    # Check if download was successful
    if [ ! -f "$MODEL_ZIP" ]; then
        echo "Warning: Vosk model download failed. You can download it manually later."
        return 1
    fi
    
    echo "Download completed, extracting model..."
    
    # Check if unzip is available
    if ! command -v unzip &> /dev/null; then
        echo "Installing unzip..."
        apt update
        apt install -y unzip
    fi
    
    # Extract the model
    if unzip -q "$MODEL_ZIP" -d "$VOSK_MODEL_DIR/"; then
        echo "Vosk model extracted successfully"
        # Clean up zip file
        rm "$MODEL_ZIP"
        echo "Vosk English model setup completed: $VOSK_MODEL_PATH"
    else
        echo "Warning: Failed to extract Vosk model. You can extract it manually later."
        echo "Extract $MODEL_ZIP to $VOSK_MODEL_DIR/"
        return 1
    fi
}

# Download Sherpa ONNX models function
download_sherpa_models() {
    echo "------------------------------------------------------------"
    echo "Checking Sherpa ONNX ASR models..."
    
    SHERPA_BASE_DIR="/opt/xiaozhi-server/models"
    SHERPA_SENSE_VOICE_DIR="$SHERPA_BASE_DIR/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17"
    SHERPA_PARAFORMER_DIR="$SHERPA_BASE_DIR/sherpa-onnx-paraformer-zh-small-2024-03-09"
    
    # Check if models are already downloaded
    SENSE_VOICE_EXISTS=false
    PARAFORMER_EXISTS=false
    
    if [ -f "$SHERPA_SENSE_VOICE_DIR/model.int8.onnx" ] && [ -f "$SHERPA_SENSE_VOICE_DIR/tokens.txt" ]; then
        SENSE_VOICE_EXISTS=true
        echo "Sherpa ONNX Sense Voice model already exists, skipping download"
    fi
    
    if [ -f "$SHERPA_PARAFORMER_DIR/model.int8.onnx" ] && [ -f "$SHERPA_PARAFORMER_DIR/tokens.txt" ]; then
        PARAFORMER_EXISTS=true
        echo "Sherpa ONNX Paraformer model already exists, skipping download"
    fi
    
    # If both models exist, skip download
    if [ "$SENSE_VOICE_EXISTS" = true ] && [ "$PARAFORMER_EXISTS" = true ]; then
        echo "All Sherpa ONNX models already exist, skipping download"
        return 0
    fi
    
    echo "Sherpa ONNX models not found, starting download..."
    
    # Download Sense Voice model if needed
    if [ "$SENSE_VOICE_EXISTS" = false ]; then
        echo "Downloading Sherpa ONNX Sense Voice model..."
        mkdir -p "$SHERPA_SENSE_VOICE_DIR"
        
        SENSE_VOICE_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2"
        SENSE_VOICE_ARCHIVE="$SHERPA_SENSE_VOICE_DIR/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2"
        
        echo "Downloading from $SENSE_VOICE_URL"
        echo "This may take several minutes depending on your internet connection..."
        
        if curl -L --progress-bar "$SENSE_VOICE_URL" -o "$SENSE_VOICE_ARCHIVE"; then
            echo "Download completed, extracting Sense Voice model..."
            
            # Check if tar is available
            if ! command -v tar &> /dev/null; then
                echo "Installing tar..."
                apt update
                apt install -y tar
            fi
            
            # Extract the model
            if tar -xjf "$SENSE_VOICE_ARCHIVE" -C "$SHERPA_SENSE_VOICE_DIR/"; then
                echo "Sense Voice model extracted successfully"
                rm "$SENSE_VOICE_ARCHIVE"
                echo "Sherpa ONNX Sense Voice model setup completed: $SHERPA_SENSE_VOICE_DIR"
            else
                echo "Warning: Failed to extract Sense Voice model"
                return 1
            fi
        else
            echo "Warning: Failed to download Sense Voice model"
            return 1
        fi
    fi
    
    # Download Paraformer model if needed
    if [ "$PARAFORMER_EXISTS" = false ]; then
        echo "Downloading Sherpa ONNX Paraformer model..."
        mkdir -p "$SHERPA_PARAFORMER_DIR"
        
        PARAFORMER_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-paraformer-zh-small-2024-03-09.tar.bz2"
        PARAFORMER_ARCHIVE="$SHERPA_PARAFORMER_DIR/sherpa-onnx-paraformer-zh-small-2024-03-09.tar.bz2"
        
        echo "Downloading from $PARAFORMER_URL"
        echo "This may take several minutes depending on your internet connection..."
        
        if curl -L --progress-bar "$PARAFORMER_URL" -o "$PARAFORMER_ARCHIVE"; then
            echo "Download completed, extracting Paraformer model..."
            
            # Extract the model
            if tar -xjf "$PARAFORMER_ARCHIVE" -C "$SHERPA_PARAFORMER_DIR/"; then
                echo "Paraformer model extracted successfully"
                rm "$PARAFORMER_ARCHIVE"
                echo "Sherpa ONNX Paraformer model setup completed: $SHERPA_PARAFORMER_DIR"
            else
                echo "Warning: Failed to extract Paraformer model"
                return 1
            fi
        else
            echo "Warning: Failed to download Paraformer model"
            return 1
        fi
    fi
    
    echo "All Sherpa ONNX models downloaded successfully!"
    echo "Models are now available for Docker deployment"
}

# Download Whisper models function
download_whisper_models() {
    echo "------------------------------------------------------------"
    echo "Checking Whisper models..."
    
    WHISPER_BASE_DIR="/opt/xiaozhi-server/models/whisper"
    
    # Check if Whisper models directory exists
    if [ ! -d "$WHISPER_BASE_DIR" ]; then
        mkdir -p "$WHISPER_BASE_DIR"
        echo "Created Whisper models directory: $WHISPER_BASE_DIR"
    fi
    
    # Define available Whisper models
    WHISPER_MODELS=(
        "tiny.en"
        "tiny"
        "base.en"
        "base"
        "small.en"
        "small"
        "medium.en"
        "medium"
        "large-v1"
        "large-v2"
        "large-v3"
    )
    
    # Check which models are already downloaded
    EXISTING_MODELS=()
    MISSING_MODELS=()
    
    for model in "${WHISPER_MODELS[@]}"; do
        MODEL_PATH="$WHISPER_BASE_DIR/$model"
        if [ -d "$MODEL_PATH" ] && [ -f "$MODEL_PATH/encoder.onnx" ] || [ -f "$MODEL_PATH/encoder.pt" ]; then
            EXISTING_MODELS+=("$model")
            echo "Whisper model '$model' already exists, skipping download"
        else
            MISSING_MODELS+=("$model")
        fi
    done
    
    # If all models exist, skip download
    if [ ${#MISSING_MODELS[@]} -eq 0 ]; then
        echo "All Whisper models already exist, skipping download"
        return 0
    fi
    
    echo "Whisper models not found, starting download..."
    echo "Available models: ${WHISPER_MODELS[*]}"
    echo "Missing models: ${MISSING_MODELS[*]}"
    
    # Note: Whisper models are downloaded automatically by the Python whisper library
    # when first used. We'll create placeholder directories and download scripts.
    echo "Creating Whisper model download setup..."
    
    # Create a Python script to download models
    cat > "$WHISPER_BASE_DIR/download_models.py" << 'EOF'
#!/usr/bin/env python3
"""
Whisper model download script
This script downloads Whisper models to the specified directory
"""
import os
import sys
import whisper
import argparse

def download_whisper_model(model_name, download_dir):
    """Download a Whisper model to the specified directory"""
    try:
        print(f"Downloading Whisper model: {model_name}")
        
        # Set the cache directory for Whisper
        os.environ['WHISPER_CACHE_DIR'] = download_dir
        
        # Load the model (this will download it if not present)
        model = whisper.load_model(model_name)
        
        print(f"Successfully downloaded Whisper model: {model_name}")
        return True
        
    except Exception as e:
        print(f"Failed to download Whisper model {model_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download Whisper models')
    parser.add_argument('--model', required=True, help='Model name to download')
    parser.add_argument('--dir', required=True, help='Download directory')
    
    args = parser.parse_args()
    
    success = download_whisper_model(args.model, args.dir)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
EOF
    
    chmod +x "$WHISPER_BASE_DIR/download_models.py"
    
    # Create a shell script for easy model downloads
    cat > "$WHISPER_BASE_DIR/download_all_models.sh" << 'EOF'
#!/bin/bash
# Whisper model download script

WHISPER_MODELS=(
    "tiny.en"
    "tiny"
    "base.en"
    "base"
    "small.en"
    "small"
    "medium.en"
    "medium"
    "large-v1"
    "large-v2"
    "large-v3"
)

DOWNLOAD_DIR="/opt/xiaozhi-server/models/whisper"

echo "Starting Whisper model downloads..."
echo "This may take a long time depending on your internet connection"
echo "Models will be downloaded to: $DOWNLOAD_DIR"

for model in "${WHISPER_MODELS[@]}"; do
    echo "Downloading model: $model"
    python3 "$DOWNLOAD_DIR/download_models.py" --model "$model" --dir "$DOWNLOAD_DIR"
    if [ $? -eq 0 ]; then
        echo "Successfully downloaded: $model"
    else
        echo "Failed to download: $model"
    fi
    echo "---"
done

echo "Whisper model download process completed"
EOF
    
    chmod +x "$WHISPER_BASE_DIR/download_all_models.sh"
    
    # Create model info file
    cat > "$WHISPER_BASE_DIR/MODELS.md" << 'EOF'
# Whisper Models

This directory contains Whisper ASR models for offline speech recognition.

## Available Models

- **tiny.en** - Fastest, English only (~39 MB)
- **tiny** - Fastest, multilingual (~39 MB)
- **base.en** - Small, English only (~74 MB)
- **base** - Small, multilingual (~74 MB)
- **small.en** - Medium, English only (~244 MB)
- **small** - Medium, multilingual (~244 MB)
- **medium.en** - Large, English only (~769 MB)
- **medium** - Large, multilingual (~769 MB)
- **large-v1** - Very large, multilingual (~1550 MB)
- **large-v2** - Very large, multilingual (~1550 MB)
- **large-v3** - Very large, multilingual (~1550 MB)

## Usage

Models are automatically downloaded when first used by the Whisper ASR provider.
You can also download them manually using the provided scripts:

```bash
# Download a specific model
python3 /opt/xiaozhi-server/models/whisper/download_models.py --model base --dir /opt/xiaozhi-server/models/whisper

# Download all models (takes a long time)
/opt/xiaozhi-server/models/whisper/download_all_models.sh
```

## Configuration

Configure Whisper models in your config.yaml:

```yaml
ASR:
  WhisperASR:
    type: whisper
    model_name: base  # Choose from available models above
    device: auto      # auto, cpu, cuda
    language: null    # null for auto-detect, or specific language code
    output_dir: tmp/
```

## Performance Notes

- **tiny/tiny.en**: Fastest, lowest accuracy, good for real-time applications
- **base/base.en**: Good balance of speed and accuracy
- **small/small.en**: Better accuracy, slower than base
- **medium/medium.en**: High accuracy, significantly slower
- **large-v1/v2/v3**: Highest accuracy, slowest processing

Choose the model based on your accuracy vs speed requirements.
EOF
    
    echo "Whisper model setup completed!"
    echo "Models will be downloaded automatically when first used"
    echo "Manual download scripts available in: $WHISPER_BASE_DIR"
    echo "Model information available in: $WHISPER_BASE_DIR/MODELS.md"
}

# Only download models if not upgrading
if [ -z "$UPGRADE_COMPLETED" ]; then
    download_vosk_model
    download_sherpa_models
    download_whisper_models
fi


# Only execute download if upgrade is not completed
if [ -z "$UPGRADE_COMPLETED" ]; then
    check_and_download "/opt/xiaozhi-server/docker-compose_all.yml" "https://raw.githubusercontent.com/lapy/xiaozhi-esp32-server/main/main/xiaozhi-server/docker-compose_all.yml"
    check_and_download "/opt/xiaozhi-server/data/.config.yaml" "https://raw.githubusercontent.com/lapy/xiaozhi-esp32-server/main/main/xiaozhi-server/config_from_api.yaml"
fi

# Start Docker service
(
echo "------------------------------------------------------------"
echo "Pulling Docker images..."
echo "This may take a few minutes, please be patient"
docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d

if [ $? -ne 0 ]; then
    whiptail --title "Error" --msgbox "Docker service startup failed, please try changing the image source and re-execute this script" 10 60
    exit 1
fi

echo "------------------------------------------------------------"
echo "Checking service startup status..."
TIMEOUT=300
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    if [ $((CURRENT_TIME - START_TIME)) -gt $TIMEOUT ]; then
        whiptail --title "Error" --msgbox "Service startup timeout, expected log content not found within specified time" 10 60
        exit 1
    fi
    
    if docker logs xiaozhi-esp32-server-web 2>&1 | grep -q "Started AdminApplication in"; then
        break
    fi
    sleep 1
done

    echo "Server started successfully! Completing configuration..."
    echo "Starting services..."
    docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d
    echo "Service startup completed!"
)

# Secret key configuration

# Get server public IP address
PUBLIC_IP=$(hostname -I | awk '{print $1}')
whiptail --title "Configure Server Secret Key" --msgbox "Please use a browser to access the following link, open the Smart Control Panel and register an account: \n\nInternal address: http://127.0.0.1:8002/\nPublic address: http://$PUBLIC_IP:8002/ (If it's a cloud server, please open ports 8000 8001 8002 in the server security group).\n\nThe first registered user is the super administrator, and subsequent users are ordinary users. Ordinary users can only bind devices and configure intelligent agents; super administrators can perform model management, user management, parameter configuration and other functions.\n\nAfter registration, please press Enter to continue" 18 70
SECRET_KEY=$(whiptail --title "Configure Server Secret Key" --inputbox "Please use the super administrator account to log into the Smart Control Panel\nInternal address: http://127.0.0.1:8002/\nPublic address: http://$PUBLIC_IP:8002/\nIn the top menu Parameter Dictionary → Parameter Management, find parameter code: server.secret (Server Secret Key) \nCopy the parameter value and enter it in the input box below\n\nPlease enter the secret key (leave empty to skip configuration):" 15 60 3>&1 1>&2 2>&3)

if [ -n "$SECRET_KEY" ]; then
    python3 -c "
import sys, yaml; 
config_path = '/opt/xiaozhi-server/data/.config.yaml'; 
with open(config_path, 'r') as f: 
    config = yaml.safe_load(f) or {}; 
config['manager-api'] = {'url': 'http://xiaozhi-esp32-server-web:8002/xiaozhi', 'secret': '$SECRET_KEY'}; 
with open(config_path, 'w') as f: 
    yaml.dump(config, f); 
"
    docker restart xiaozhi-esp32-server
fi

# Get and display address information
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Fix log file unable to get ws issue, change to hardcode
whiptail --title "Installation Complete!" --msgbox "\
Server related addresses are as follows:\n\
Management backend access address: http://$LOCAL_IP:8002\n\
OTA address: http://$LOCAL_IP:8003/xiaozhi/ota/\n\
Vision analysis interface address: http://$LOCAL_IP:8003/mcp/vision/explain\n\
WebSocket address: ws://$LOCAL_IP:8000/xiaozhi/v1/\n\
\nInstallation complete! Thank you for using!\nPress Enter to exit..." 16 70
