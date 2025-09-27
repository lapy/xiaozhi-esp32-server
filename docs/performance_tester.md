# Performance Testing Tool Usage Guide for Speech Recognition, Large Language Models, Non-streaming Speech Synthesis, Streaming Speech Synthesis, and Vision Models

1. Create data directory under main/xiaozhi-server directory
2. Create .config.yaml file under data directory
3. In .data/config.yaml, write your speech recognition, large language model, streaming speech synthesis, vision model parameters
For example:
```
LLM:
  ChatGLMLLM:
    # Define LLM API type
    type: openai
    # glm-4-flash is free, but still needs to register and fill in api_key
    # You can find your api key here https://bigmodel.cn/usercenter/proj-mgmt/apikeys
    model_name: glm-4-flash
    url: https://open.bigmodel.cn/api/paas/v4/
    api_key: your_chat_glm_web_key

TTS:

VLLM:

ASR:
  WhisperASR:
    type: whisper
    model_name: base
    device: auto
    language: null
    output_dir: tmp/
```
4. Run performance_tester.py under main/xiaozhi-server directory: 
```
python performance_tester.py
```