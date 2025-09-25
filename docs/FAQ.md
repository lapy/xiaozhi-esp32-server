# Frequently Asked Questions ❓

### 1. Why does Xiaozhi recognize multiple languages when I speak? 🌍

Suggestion: Check if the `models/SenseVoiceSmall` directory has a `model.pt` file. If not, download it from [here](Deployment.md#model-files).

### 2. Why does the error "TTS task failed: file not found" occur? 📁

Suggestion: Check if you have installed `libopus` and `ffmpeg` using `conda`. If not, install them.

### 3. Why does the TTS task often fail and timeout? ⏰

Suggestion: If TTS often fails, please check if you are using a proxy. If so, try disabling the proxy and retrying.

### 4. Why can't I connect to the self-built server using 4G mode? 🔐

Reason: The firmware of the ESP32 board requires a secure connection in 4G mode.

Solution: There are two ways to solve this problem. You can either modify the code to use a secure connection or use nginx to configure an SSL certificate. Refer to [this tutorial](https://icnt94i5ctj4.feishu.cn/docx/GnYOdMNJOoRCljx1ctecsj9cnRe) for more information.

### 5. How can I improve the response speed of Xiaozhi? ⚡

Suggestion: The default configuration of this project is a low-cost solution. We recommend that beginners use the default free model to solve the "running" problem first, and then optimize the "running fast" problem. You can try replacing each module with a faster one. Since version `0.5.2`, the project supports streaming configuration, which can improve the response speed by about `2.5` seconds compared to the early version.

| Module Name | Default Free Configuration | Streaming Configuration |
|:---:|:---:|:---:|
| ASR (Speech Recognition) | OpenaiASR (API) | 👍OpenaiASR (API) or 👍GroqASR (API) |
| LLM (Large Model) | ChatGLMLLM (ZhIPu glm-4-flash) | 👍AliLLM (qwen3-235b-a22b-instruct-2507) |
| VLLM (Visual Large Model) | ChatGLMVLLM (ZhIPu glm-4v-flash) | 👍QwenVLVLLM (Qwen qwen2.5-vl-3b-instructh) |
| TTS (Text-to-Speech) | ✅EdgeTTS (Microsoft Edge TTS) | 👍OpenAITTS (OpenAI TTS) |
| Intent (Intent Recognition) | function_call (Function Call) | function_call (Function Call) |
| Memory (Memory Function) | mem_local_short (Local Short-term Memory) | mem_local_short (Local Short-term Memory) |

If you are concerned about the execution time of each module, please refer to [the performance test report](https://github.com/xinnan-tech/xiaozhi-performance-research) and test it in your environment according to the report.

### 6. Why does Xiaozhi often repeat my words when I speak slowly? 🗣️

Suggestion: In the configuration file, find the following part and increase the value of `min_silence_duration_ms` (e.g., to `1000`):
```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700  # If you speak slowly, you can increase this value
```
### 7. Deployment-related tutorials

1. [How to deploy the project with minimal configuration](./Deployment.md)<br/>
2. [How to deploy the project with full configuration](./Deployment_all.md)<br/>
3. [How to deploy the MQTT gateway and enable MQTT+UDP protocol](./mqtt-gateway-integration.md)<br/>
4. [How to automatically pull the latest code and compile and start the project](./dev-ops-integration.md)<br/>
5. [How to integrate with Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>

### 8. Firmware-related tutorials

1. [How to compile the firmware yourself](./firmware-build.md)<br/>
2. [How to modify the OTA address based on the firmware compiled](./firmware-setting.md)<br/>

### 9. Expansion-related tutorials

1. [How to enable phone number registration](./ali-sms-integration.md)<br/>
2. [How to integrate with HomeAssistant to control smart home devices](./homeassistant-integration.md)<br/>
3. [How to enable visual models to recognize objects](./mcp-vision-integration.md)<br/>
4. [How to deploy the MCP endpoint](./mcp-endpoint-enable.md)<br/>
5. [How to integrate with the MCP endpoint](./mcp-endpoint-integration.md)<br/>
6. [How to enable voiceprint recognition](./voiceprint-integration.md)<br/>

### 10. Performance testing tutorials

1. [Performance testing tutorial for each module](./performance_tester.md)<br/>
2. [Regularly published performance test results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>

### 13. More questions? Contact us! 💬

You can submit your questions in [issues](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues).