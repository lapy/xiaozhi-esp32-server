# Docker Rebuild Instructions

## ⚠️ Critical Fix Applied
**PortAudio library** has been added to `Dockerfile-server` to fix the audio processing error:
```
ERROR-Failed to instantiate components: PortAudio library not found
```

## 🔧 Rebuild Steps

### Option 1: Using docker-compose (Recommended)
```bash
# Stop running containers
docker-compose down

# Rebuild with no cache to ensure fresh build
docker-compose build --no-cache

# Start the services
docker-compose up -d

# Check logs
docker-compose logs -f xiaozhi-esp32-server
```

### Option 2: Using docker directly
```bash
# Stop and remove old container
docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

# Remove old image (optional but recommended)
docker rmi xiaozhi-esp32-server

# Rebuild from project root
docker build --no-cache -t xiaozhi-esp32-server -f Dockerfile-server .

# Run new container
docker run -d --name xiaozhi-esp32-server -p 8000:8000 xiaozhi-esp32-server

# Check logs
docker logs -f xiaozhi-esp32-server
```

## ✅ What Was Fixed

### Dockerfile-server Changes:
- Added **portaudio19-dev** (development headers)
- Added **libportaudio2** (runtime library)
- Added **libportaudiocpp0** (C++ bindings)

These libraries are required for PyAudio and other audio processing components.

## 🎯 Expected Result

After rebuilding, you should see:
- ✅ TTS initialization successful
- ✅ LLM provider initialized
- ✅ Audio processing working
- ✅ No more "PortAudio library not found" errors

## 📋 Verification

Once rebuilt, test by checking logs for:
```bash
# Should see successful initialization
docker-compose logs xiaozhi-esp32-server | grep "TTS"
docker-compose logs xiaozhi-esp32-server | grep "initialization completed"

# Should NOT see PortAudio errors
docker-compose logs xiaozhi-esp32-server | grep "PortAudio"
```

## 🐛 If Issues Persist

1. **Verify Dockerfile-server has PortAudio libs**:
   - Check lines 22-31 contain portaudio19-dev, libportaudio2, libportaudiocpp0

2. **Clean rebuild**:
   ```bash
   docker-compose down -v
   docker system prune -f
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Check container has libraries**:
   ```bash
   docker exec xiaozhi-esp32-server dpkg -l | grep portaudio
   ```
   Should show:
   - libportaudio2
   - portaudio19-dev (if builder stage kept)

## 📦 Updated Files

The following files were updated and need to be deployed to your Docker machine:
- ✅ `Dockerfile-server` - Added PortAudio dependencies
- ✅ `main/xiaozhi-server/requirements.txt` - All Python deps updated to latest 2025 versions
- ✅ `main/xiaozhi-server/core/providers/tts/elevenlabs.py` - ElevenLabs integration
- ✅ `main/xiaozhi-server/core/providers/tts/kokoro.py` - Kokoro TTS integration
- ✅ `main/xiaozhi-server/config.yaml` - Added ElevenLabs & Kokoro configs
- ✅ Database migrations in `main/manager-api/src/main/resources/db/changelog/`

## 🎉 Summary

**Root Cause**: Docker container was missing PortAudio system libraries required for audio processing.

**Fix**: Updated `Dockerfile-server` to install PortAudio libraries (portaudio19-dev, libportaudio2, libportaudiocpp0).

**Action Required**: Rebuild Docker container on your remote machine using the commands above.

