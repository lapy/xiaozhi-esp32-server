# Vision Model Usage Guide
This tutorial is divided into two parts:
- Part 1: Running xiaozhi-server in single module mode to enable vision model
- Part 2: How to enable vision model when running in full module mode

Before enabling the vision model, you need to prepare three things:
- You need to prepare a device with a camera, and this device is already in the repository with camera functionality implemented. For example, `LCSC ESP32-S3 Development Board`
- Your device firmware version is upgraded to 1.6.6 or above
- You have successfully run the basic conversation module

## Single Module Running xiaozhi-server to Enable Vision Model

### Step 1: Confirm Network
Since the vision model will start port 8003 by default.

If you are running with docker, please confirm whether your `docker-compose.yml` has port `8003`, if not, update to the latest `docker-compose.yml` file

If you are running with source code, confirm whether the firewall allows port `8003`

### Step 2: Choose Your Vision Model
Open your `data/.config.yaml` file and set your `selected_module.VLLM` to a vision model. Currently we support vision models with `openai` type interfaces. `OpenAILLMVLLM` is one of the models compatible with `openai`.

```
selected_module:
  VAD: ..
  ASR: ..
  LLM: ..
  VLLM: OpenAILLMVLLM
  TTS: ..
  Memory: ..
  Intent: ..
```

Assuming we use `OpenAILLMVLLM` as the vision model, we need to first log in to the [OpenAI](https://platform.openai.com/api-keys) website to apply for an API key. If you have already applied for a key before, you can reuse that key.

In your configuration file, add this configuration. If you already have this configuration, set up your api_key.

```
VLLM:
  OpenAILLMVLLM:
    api_key: your_api_key
```

### Step 3: Start xiaozhi-server service
If you are using source code, enter the command to start
```
python app.py
```
If you are running with docker, restart the container
```
docker restart xiaozhi-esp32-server
```

After starting, it will output logs with the following content.

```
2025-06-01 **** - OTA interface is           http://192.168.4.7:8003/xiaozhi/ota/
2025-06-01 **** - Vision analysis interface is        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket address is       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======The above addresses are websocket protocol addresses, do not access with browser=======
2025-06-01 **** - If you want to test websocket, please use Google Chrome to open test_page.html in the test directory
2025-06-01 **** - =============================================================
```

After starting, use your browser to open the `Vision analysis interface` connection in the logs. See what it outputs? If you are on Linux and don't have a browser, you can execute this command:
```
curl -i your_vision_analysis_interface
```

Normally it will display like this
```
MCP Vision interface is running normally, vision explanation interface address is: http://xxxx:8003/mcp/vision/explain
```

Please note, if you are using public network deployment or docker deployment, you must change this configuration in your `data/.config.yaml`
```
server:
  vision_explain: http://your_IP_or_domain:port_number/mcp/vision/explain
```

Why? Because the vision explanation interface needs to be distributed to the device. If your address is a local network address or a docker internal address, the device cannot access it.

Assuming your public network address is `111.111.111.111`, then `vision_explain` should be configured like this

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

If your MCP Vision interface is running normally, and you have also tried to access the distributed `Vision explanation interface address` normally with your browser, please continue to the next step

### Step 4: Device Wake-up Activation

Say to the device "Please turn on the camera and tell me what you see"

Pay attention to the xiaozhi-server log output to see if there are any errors.


## How to enable vision model when running full module

### Step 1: Confirm Network
Since the vision model will start port 8003 by default.

If you are running with docker, please confirm whether your `docker-compose_all.yml` maps port `8003`. If not, update to the latest `docker-compose_all.yml` file

If you are running from source code, confirm whether the firewall allows port `8003`

### Step 2: Confirm Your Configuration File

Open your `data/.config.yaml` file and confirm whether the structure of your configuration file is the same as `data/config_from_api.yaml`. If it's different or missing something, please complete it.

### Step 3: Configure Vision Model API Key

We need to first log in to the [OpenAI](https://platform.openai.com/api-keys) website to apply for an API key. If you have already applied for a key before, you can reuse that key.

Log in to the `Smart Control Panel`, click `Model Configuration` in the top menu, click `Vision Large Language Model` in the left sidebar, find `VLLM_OpenAILLMVLLM`, click the modify button, enter your API key in the `API Key` field in the popup, and click save.

After saving successfully, go to the agent you need to test, click `Configure Role`, in the opened content, check whether `Vision Large Language Model (VLLM)` has selected the vision model just configured. Click save.

### Step 4: Start xiaozhi-server module
If you are using source code, enter the command to start
```
python app.py
```
If you are running with docker, restart the container
```
docker restart xiaozhi-esp32-server
```

After starting, it will output logs with the following content.

```
2025-06-01 **** - Vision analysis interface is        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket address is       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======The above addresses are websocket protocol addresses, do not access with browser=======
2025-06-01 **** - If you want to test websocket, please use Google Chrome to open test_page.html in the test directory
2025-06-01 **** - =============================================================
```

After starting, use your browser to open the `Vision analysis interface` connection in the logs. See what it outputs? If you are on Linux and don't have a browser, you can execute this command:
```
curl -i your_vision_analysis_interface
```

Normally it will display like this
```
MCP Vision interface is running normally, vision explanation interface address is: http://xxxx:8003/mcp/vision/explain
```

Please note, if you are using public network deployment or docker deployment, you must change this configuration in your `data/.config.yaml`
```
server:
  vision_explain: http://your_IP_or_domain:port_number/mcp/vision/explain
```

Why? Because the vision explanation interface needs to be distributed to the device. If your address is a local network address or a docker internal address, the device cannot access it.

Assuming your public network address is `111.111.111.111`, then `vision_explain` should be configured like this

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

If your MCP Vision interface is running normally, and you have also tried to access the distributed `Vision explanation interface address` normally with your browser, please continue to the next step

### Step 4: Device Wake-up Activation

Say to the device "Please turn on the camera and tell me what you see"

Pay attention to the xiaozhi-server log output to see if there are any errors.
