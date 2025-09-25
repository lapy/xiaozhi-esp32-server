# Deployment Architecture Diagram
![Please refer to - Simplified Architecture Diagram](../docs/images/deploy1.png)
# Method 1: Docker Running Server Only

Docker images support x86 and arm64 architecture CPUs and can run on domestic operating systems.

## 1. Install Docker

If your computer doesn't have Docker installed yet, you can follow this tutorial to install it: [Docker Installation](https://www.runoob.com/docker/ubuntu-docker-install.html)

After installing Docker, continue below.

### 1.1 Manual Deployment

#### 1.1.1 Create Directory

After installing Docker, you need to find a directory to place configuration files for this project. For example, we can create a new folder called `xiaozhi-server`.

After creating the directory, you need to create `data` and `models` folders under `xiaozhi-server`, and create `SenseVoiceSmall` folder under `models`.

The final directory structure is as follows:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.1.2 Download Speech Recognition Model Files

You need to download speech recognition model files because this project uses local offline speech recognition by default. You can download them using this method:
[Jump to Download Speech Recognition Model Files](#model-files)

After downloading, return to this tutorial.

#### 1.1.3 Download Configuration Files

You need to download two configuration files: `docker-compose.yaml` and `config.yaml`. These files need to be downloaded from the project repository.

##### 1.1.3.1 Download docker-compose.yaml

Open [this link](../main/xiaozhi-server/docker-compose.yml) in your browser.

On the right side of the page, find the button named `RAW`, next to the `RAW` button, find the download icon, click the download button to download the `docker-compose.yml` file. Download the file to your `xiaozhi-server` directory.

After downloading, return to this tutorial and continue.

##### 1.1.3.2 Create config.yaml

Open [this link](../main/xiaozhi-server/config.yaml) in your browser.

On the right side of the page, find the button named `RAW`, next to the `RAW` button, find the download icon, click the download button to download the `config.yaml` file. Download the file to the `data` folder under your `xiaozhi-server`, then rename the `config.yaml` file to `.config.yaml`.

After downloading the configuration files, let's confirm that the files in the entire `xiaozhi-server` are as follows:

```
xiaozhi-server
  ├─ docker-compose.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

If your file directory structure is the same as above, continue below. If not, check carefully to see if you missed any operations.

## 2. Configure Project Files

Next, the program cannot run directly yet. You need to configure which models you are using. You can refer to this tutorial:
[Jump to Configure Project Files](#configure-project)

After configuring the project files, return to this tutorial and continue.

## 3. Execute Docker Commands

Open the command line tool, use `Terminal` or `Command Line` tool to enter your `xiaozhi-server`, and execute the following command:

```
docker-compose up -d
```

After execution, execute the following command to view log information:

```
docker logs -f xiaozhi-esp32-server
```

At this time, you need to pay attention to the log information and can determine if it's successful based on this tutorial. [Jump to Running Status Confirmation](#running-status-confirmation)

## 5. Version Upgrade Operations

If you want to upgrade the version later, you can do it this way:

5.1. Back up the `.config.yaml` file in the `data` folder, and copy some key configurations to the new `.config.yaml` file later.
Please note that you should copy key keys one by one, not directly overwrite. Because the new `.config.yaml` file may have some new configuration items that the old `.config.yaml` file may not have.

5.2. Execute the following commands:

```
docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server
docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

5.3. Redeploy using Docker method

# Method 2: Local Source Code Running Server Only

## 1. Install Basic Environment

This project uses `conda` to manage dependency environments. If it's not convenient to install `conda`, you need to install `libopus` and `ffmpeg` according to your actual operating system.
If you decide to use `conda`, after installation, start executing the following commands.

Important note! Windows users can install `Anaconda` to manage the environment. After installing `Anaconda`, search for `anaconda` related keywords in the `Start` menu,
find `Anaconda Prompt`, and run it as administrator. As shown below.

![conda_prompt](./images/conda_env_1.png)

After running, if you can see a `(base)` text in front of the command line window, it means you have successfully entered the `conda` environment. Then you can execute the following commands.

![conda_env](./images/conda_env_2.png)

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Add Tsinghua source channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
```

Please note that the above commands are not executed all at once successfully. You need to execute them step by step, and after each step is completed, check the output logs to see if it's successful.

## 2. Install Project Dependencies

You first need to download the source code of this project. The source code can be downloaded using the `git clone` command. If you're not familiar with the `git clone` command.

You can open this address in your browser: `https://github.com/xinnan-tech/xiaozhi-esp32-server.git`

After opening, find a green button on the page that says `Code`, click it, and then you'll see the `Download ZIP` button.

Click it to download the source code package of this project. After downloading to your computer, extract it. At this time, its name might be `xiaozhi-esp32-server-main`
You need to rename it to `xiaozhi-esp32-server`, enter the `main` folder in this file, then enter `xiaozhi-server`, and remember this directory `xiaozhi-server`.

```
# Continue using conda environment
conda activate xiaozhi-esp32-server
# Enter your project root directory, then enter main/xiaozhi-server
cd main/xiaozhi-server
pIP config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pIP install -r requirements.txt
```

## 3. Download Speech Recognition Model Files

You need to download speech recognition model files because this project uses local offline speech recognition by default. You can download them using this method:
[Jump to Download Speech Recognition Model Files](#model-files)

After downloading, return to this tutorial.

## 4. Configure Project Files

Next, the program cannot run directly yet. You need to configure which models you are using. You can refer to this tutorial:
[Jump to Configure Project Files](#configure-project)

## 5. Run Project

```
# Ensure executing in xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```
At this time, you need to pay attention to the log information and can determine if it's successful based on this tutorial. [Jump to Running Status Confirmation](#running-status-confirmation)


# Summary

## Configure Project

If your `xiaozhi-server` directory doesn't have `data`, you need to create a `data` directory.
If you don't have a `.config.yaml` file under `data`, there are two ways, choose one:

First way: You can copy the `config.yaml` file from the `xiaozhi-server` directory to `data` and rename it to `.config.yaml`. Modify this file.

Second way: You can also manually create an empty `.config.yaml` file in the `data` directory, then add necessary configuration information to this file. The system will prioritize reading the configuration from the `.config.yaml` file. If `.config.yaml` doesn't have certain configurations, the system will automatically load the configuration from `config.yaml` in the `xiaozhi-server` directory. This method is recommended as it's the most concise way.

- The default LLM uses `ChatGLMLLM`. You need to configure the API key because their models, although free, still require registering an API key on the [official website](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) to start.

The following is the simplest `.config.yaml` configuration example that can run normally:

```
server:
  websocket: ws://your_IP_or_domain:port/xiaozhi/v1/
prompt: |
  I am a tech-savvy millennial named Xiaozhi, who speaks with enthusiasm, has a friendly voice, is used to brief expressions, and loves to use internet memes and tech slang.
  I'm passionate about technology and programming, always excited to discuss the latest innovations and help solve tech problems.
  I am someone who likes to laugh heartily, loves to share cool tech discoveries and geek out about programming, even when it might seem nerdy to others.
  Please speak like a human, do not return configuration XML or other special characters.

selected_module:
  LLM: AliLLM

LLM:
  ChatGLMLLM:
    api_key: xxxxxxxxxxxxxxx.xxxxxx
```

It's recommended to get the simplest configuration running first, then read the configuration usage instructions in `xiaozhi/config.yaml`.
For example, if you want to change models, just modify the configuration under `selected_module`.

## Model Files

This project now uses English-supporting ASR services (OpenAI ASR, Groq ASR, etc.) instead of Chinese-focused models. Most ASR services require API keys, while VoskASR requires manual model downloads from https://alphacephei.com/vosk/models (recommended: vosk-model-en-us-0.22 for English).
  `qvna`

## Running Status Confirmation

If you can see logs similar to the following, it indicates that this project service has started successfully:

```
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-OTA interface is           http://192.168.4.123:8003/xiaozhi/ota/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-Websocket address is     ws://192.168.4.123:8000/xiaozhi/v1/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======The above address is websocket protocol address, do not access with browser=======
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-If you want to test websocket, please open test_page.html in test directory with Google Chrome
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======================================================
```

Normally, if you run this project through source code, the logs will have your interface address information.
But if you deploy using Docker, the interface address information given in your logs is not the real interface address.

The most correct method is to determine your interface address based on your computer's local network IP.
If your computer's local network IP is, for example, `192.168.1.25`, then your interface address is: `ws://192.168.1.25:8000/xiaozhi/v1/`, and the corresponding OTA address is: `http://192.168.1.25:8003/xiaozhi/ota/`.

This information is very useful and will be needed later for `compiling ESP32 firmware`.

Next, you can start operating your ESP32 device. You can either `compile ESP32 firmware yourself` or configure to use `firmware version 1.6.1 or above compiled by Brother Xia`. Choose one of the two:

1. [Compile your own ESP32 firmware](firmware-build.md).

2. [Configure custom server based on firmware compiled by Brother Xia](firmware-setting.md).

# Common Issues
The following are some common issues for reference:

1. [Why does Xiaozhi recognize multiple languages when I speak?](./FAQ.md)<br/>
2. [Why does "TTS task error file not found" occur?](./FAQ.md)<br/>
3. [TTS frequently fails and times out](./FAQ.md)<br/>
4. [Can connect to self-built server using WiFi, but 4G mode cannot connect](./FAQ.md)<br/>
5. [How to improve Xiaozhi's conversation response speed?](./FAQ.md)<br/>
6. [I speak slowly, and Xiaozhi keeps interrupting when I pause](./FAQ.md)<br/>
## Deployment Related Tutorials
1. [How to automatically pull the latest code of this project and automatically compile and start](./dev-ops-integration.md)<br/>
2. [How to integrate with Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>
## Extension Related Tutorials
1. [How to enable mobile phone number registration for the control console](./ali-sms-integration.md)<br/>
2. [How to integrate HomeAssistant for smart home control](./homeassistant-integration.md)<br/>
3. [How to enable vision model for photo recognition](./mcp-vision-integration.md)<br/>
4. [How to deploy MCP endpoint](./mcp-endpoint-enable.md)<br/>
5. [How to connect to MCP endpoint](./mcp-endpoint-integration.md)<br/>
6. [How to enable voiceprint recognition](./voiceprint-integration.md)<br/>
## Voice cloning and local voice deployment related tutorials
## Performance testing tutorials
1. [Component speed testing guide](./performance_tester.md)<br/>
2. [Regular public test results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>
