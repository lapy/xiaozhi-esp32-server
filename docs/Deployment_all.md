# Deployment Architecture Diagram
![Please refer to - Full Module Installation Architecture Diagram](../docs/images/deploy2.png)
# Method 1: Run All Modules with Docker
Docker images support x86 and arm64 CPU architectures and can run on domestic operating systems.

## 1. Install Docker

If your computer does not have Docker installed, follow this tutorial: [Docker Installation](https://www.runoob.com/docker/ubuntu-docker-install.html)

There are two ways to install and run all modules with Docker. You can [use the one-click scrIPt](./Deployment_all.md#11-one-click-scrIPt) (by [@VanillaNahida](https://github.com/VanillaNahida)).  
The scrIPt will automatically download the required images and configuration files for you. Alternatively, you can use [manual deployment](./Deployment_all.md#12-manual-deployment) to set everything up from scratch.



### 1.1 One-Click ScrIPt
Easy deployment. You can refer to the [video tutorial](https://www.bilibili.com/video/BV17bbvzHExd/). The written tutorial is as follows:
> [!NOTE]  
> Currently supports one-click deployment on Ubuntu servers only. Other systems are not tested and may have unexpected issues.

Use an SSH tool to connect to the server and execute the following scrIPt as root:
```bash
sudo bash -c "$(wget -qO- https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/docker-setup.sh)"
```

The scrIPt will automatically perform the following actions:
> 1. Install Docker
> 2. Configure registry mirrors
> 3. Pull Docker images
> 4. Download the speech recognition model files
> 5. Guide you through server configuration
>

After completion and a brief configuration, refer to [4. Run the program](#4-run-the-program) and [5. Restart xiaozhi-esp32-server](#5-restart-xiaozhi-esp32-server) for the three most important tasks. Once those three are configured, you can start using the system.

### 1.2 Manual Deployment

#### 1.2.1 Create Directories

After installation, create a directory to store this project's configuration files, for example `xiaozhi-server`.

Inside `xiaozhi-server`, create `data` and `models` folders for other model files.

Final structure:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ (other model directories as needed)
```

#### 1.2.2 Download Speech Recognition Model File

This project now uses English-supporting ASR services (OpenAI ASR, Groq ASR, etc.) instead of Chinese-focused models. Most ASR services require API keys, while VoskASR requires manual model downloads from https://alphacephei.com/vosk/models (recommended: vosk-model-en-us-0.22 for English).

**For VoskASR (Recommended for English):**

1. **Download the Vosk English Model:**
   - Visit the official Vosk models page: https://alphacephei.com/vosk/models
   - Download the English model: `vosk-model-en-us-0.22.zip` (approximately 1.8 GB)
   - For smaller systems, you can use `vosk-model-small-en-us-0.15.zip` (approximately 40 MB)

2. **Extract the Model:**
   ```bash
   # Navigate to your xiaozhi-server directory
   cd xiaozhi-server
   
   # Create a vosk directory inside models
   mkdir -p models/vosk
   
   # Extract the downloaded model to the vosk directory
   # Replace 'vosk-model-en-us-0.22.zip' with the actual filename you downloaded
   unzip vosk-model-en-us-0.22.zip -d models/vosk/
   ```

3. **Verify the Model Structure:**
   After extraction, your directory structure should look like:
   ```
   xiaozhi-server
     ├─ data
     ├─ models
        ├─ vosk
           ├─ vosk-model-en-us-0.22
              ├─ am
              ├─ graph
              ├─ ivector
              └─ conf
   ```

4. **Configure the Model Path:**
   In your `.config.yaml` file (located in the `data` folder), set the correct model path:
   ```yaml
   selected_module:
     ASR: VoskASR
   
   ASR:
     VoskASR:
       type: vosk
       model_path: models/vosk/vosk-model-en-us-0.22
       output_dir: tmp/
   ```


#### 1.2.3 Download Configuration Files

You need to download two configuration files: `docker-compose_all.yaml` and `config_from_api.yaml`. These files need to be downloaded from the project repository.

##### 1.2.3.1 Download docker-compose_all.yaml

Open [this link](../main/xiaozhi-server/docker-compose_all.yml) in your browser.

On the right side of the page, find the button named `RAW`. Next to the `RAW` button, find the download icon and click the download button to download the `docker-compose_all.yml` file. Download the file to your
`xiaozhi-server` directory.

Alternatively, execute `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml` to download directly.

After downloading, return to this tutorial and continue.

##### 1.2.3.2 Download config_from_api.yaml

Open [this link](../main/xiaozhi-server/config_from_api.yaml) in your browser.

On the right side of the page, find the button named `RAW`. Next to the `RAW` button, find the download icon and click the download button to download the `config_from_api.yaml` file. Download the file to the
`data` folder under your `xiaozhi-server` directory, then rename the `config_from_api.yaml` file to `.config.yaml`.

Alternatively, execute `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml` to download and save.

After downloading the configuration files, let's confirm that the files in the entire `xiaozhi-server` directory are as follows:

```
xiaozhi-server
  ├─ docker-compose_all.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ (other model directories as needed)
       ├─ model.pt
```

If your file directory structure matches the above, continue. If not, carefully check if you missed any operations.

## 2. Backup Data

If you have previously successfully run the Smart Control Panel and have important key information saved, please first copy the important data from the Smart Control Panel. During the upgrade process, the original data may be overwritten.

## 3. Clean Up Historical Version Images and Containers
Next, open the command line tool, use `Terminal` or `Command Line` tool to enter your `xiaozhi-server` directory, and execute the following commands

```
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

## 4. Run the Program
Execute the following command to start the new version containers

```
docker compose -f docker-compose_all.yml up -d
```

After execution, run the following command to view log information.

```
docker logs -f xiaozhi-esp32-server-web
```

When you see the output logs, it means your `Smart Control Panel` has started successfully.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

Please note that at this moment only the `Smart Control Panel` can run. If port 8000 `xiaozhi-esp32-server` reports an error, don't worry about it for now.

At this time, you need to use a browser to open the `Smart Control Panel`, link: http://127.0.0.1:8002, and register the first user. The first user is the super administrator, and subsequent users are ordinary users. Ordinary users can only bind devices and configure intelligent agents; super administrators can perform model management, user management, parameter configuration and other functions.

Next, you need to do three important things:

### The First Important Thing

Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the first data entry in the list with parameter code `server.secret`, and copy its `Parameter Value`.

`server.secret` needs some explanation. This `Parameter Value` is very important, as it allows our `Server` side to connect to `manager-api`. `server.secret` is a key that is automatically randomly generated each time the manager module is deployed from scratch.

After copying the `Parameter Value`, open the `.config.yaml` file in the `data` directory under `xiaozhi-server`. At this moment, your configuration file content should look like this:

```
manager-api:
  url:  http://127.0.0.1:8002/xiaozhi
  secret: your_server_secret_value
```
1. Copy the `Parameter Value` of `server.secret` that you just copied from the `Smart Control Panel` into the `secret` field in the `.config.yaml` file.

2. Since you are using Docker deployment, change the `url` to `http://xiaozhi-esp32-server-web:8002/xiaozhi`

The result should look like this:
```
manager-api:
  url: http://xiaozhi-esp32-server-web:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

After saving, continue with the second important thing.

### The Second Important Thing

Using the super administrator account, log into the Smart Control Panel, find `Model Configuration` in the top menu, then click `Large Language Model` in the left sidebar, find the first data entry `ZhIPu AI`, click the `Modify` button,
After the modification dialog pops up, fill in the key of `ZhIPu AI` that you registered into the `API Key` field. Then click save.

## 5. Restart xiaozhi-esp32-server

Next, open the command line tool, use `Terminal` or `Command Line` tool to input
```
docker restart xiaozhi-esp32-server
docker logs -f xiaozhi-esp32-server
```
If you can see logs similar to the following, it indicates that the Server has started successfully.

```
25-02-23 12:01:09[core.websocket_server] - INFO - Websocket address is      ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======The above address is a websocket protocol address, please do not access it with a browser=======
25-02-23 12:01:09[core.websocket_server] - INFO - To test websocket, please use Google Chrome to open test_page.html in the test directory
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Since you are deploying all modules, you have two important interfaces that need to be written into the ESP32.

OTA Interface:
```
http://your-host-machine-lan-IP:8003/xiaozhi/ota/
```

Websocket Interface:
```
ws://your-host-machine-IP:8000/xiaozhi/v1/
```

### The Third Important Thing

Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the parameter code `server.websocket`, and input your `Websocket Interface`.

Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the parameter code `server.ota`, and input your `OTA Interface`.

Next, you can start operating your ESP32 device. You can either `compile your own ESP32 firmware` or configure to use `Xiage's pre-compiled firmware version 1.6.1 or above`. Choose one of the two options:

1. [Compile your own ESP32 firmware](firmware-build.md).

2. [Configure custom server based on Xiage's pre-compiled firmware](firmware-setting.md).


# Method 2: Run All Modules with Local Source Code

## 1. Install MySQL Database

If MySQL is already installed on your machine, you can directly create a database named `xiaozhi_esp32_server` in the database.

```sql
CREATE DATABASE xiaozhi_esp32_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

If you don't have MySQL yet, you can install MySQL through Docker

```
docker run --name xiaozhi-esp32-server-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -e MYSQL_DATABASE=xiaozhi_esp32_server -e MYSQL_INITDB_ARGS="--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci" -e TZ=Asia/Shanghai -d mysql:latest
```

## 2. Install Redis

If you don't have Redis yet, you can install Redis through Docker

```
docker run --name xiaozhi-esp32-server-redis -d -p 6379:6379 redis
```

## 3. Run manager-api Program

3.1 Install JDK21, set JDK environment variables

3.2 Install Maven, set Maven environment variables

3.3 Use VSCode programming tool, install Java environment related plugins

3.4 Use VSCode programming tool to load the manager-api module

Configure database connection information in `src/main/resources/application-dev.yml`

```
spring:
  datasource:
    username: root
    password: 123456
```
Configure Redis connection information in `src/main/resources/application-dev.yml`
```
spring:
    data:
      redis:
        host: localhost
        port: 6379
        password:
        database: 0
```

3.5 Run Main Program

This project is a SpringBoot project. The startup method is:
Open `Application.java` and run the `Main` method to start

```
Path address:
src/main/java/xiaozhi/AdminApplication.java
```

When you see the output logs, it means your `manager-api` has started successfully.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

## 4. Run manager-web Program

4.1 Install Node.js

4.2 Use VSCode programming tool to load the manager-web module

Use terminal commands to enter the manager-web directory

```
npm install
```
Then start
```
npm run serve
```

Please note, if your manager-api interface is not at `http://localhost:8002`, please modify the path in
`main/manager-web/.env.development` during development.

After successful operation, you need to use a browser to open the `Smart Control Panel`, link: http://127.0.0.1:8001, and register the first user. The first user is the super administrator, and subsequent users are ordinary users. Ordinary users can only bind devices and configure intelligent agents; super administrators can perform model management, user management, parameter configuration and other functions.


Important: After successful registration, use the super administrator account to log into the Smart Control Panel, find `Model Configuration` in the top menu, then click `Large Language Model` in the left sidebar, find the first data entry `ZhIPu AI`, click the `Modify` button,
After the modification dialog pops up, fill in the key of `ZhIPu AI` that you registered into the `API Key` field. Then click save.

## 5. Install Python Environment

This project uses `conda` to manage dependency environments. If it's inconvenient to install `conda`, you need to install `libopus` and `ffmpeg` according to your actual operating system.
If you decide to use `conda`, after installation, start executing the following commands.

Important note! For Windows users, you can manage the environment by installing `Anaconda`. After installing `Anaconda`, search for `anaconda` related keywords in `Start`,
find `Anaconda Prompt`, and run it as administrator. As shown below.

![conda_prompt](./images/conda_env_1.png)

After running, if you can see a (base) label in front of the command line window, it means you have successfully entered the `conda` environment. Then you can execute the following commands.

![conda_env](./images/conda_env_2.png)

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Add Tsinghua mirror channels
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
```

Please note that the above commands are not executed all at once to be successful. You need to execute them step by step, and after each step is completed, check the output logs to see if it was successful.

## 6. Install Project Dependencies

You first need to download the project source code. The source code can be downloaded through the `git clone` command. If you are not familiar with the `git clone` command.

You can open this address in your browser: `https://github.com/xinnan-tech/xiaozhi-esp32-server.git`

After opening, find a green button on the page that says `Code`, click on it, and then you will see the `Download ZIP` button.

Click on it to download the project source code archive. After downloading to your computer, extract it. At this time, its name might be `xiaozhi-esp32-server-main`
You need to rename it to `xiaozhi-esp32-server`. In this file, enter the `main` folder, then enter `xiaozhi-server`. Please remember this directory `xiaozhi-server`.

```
# Continue using conda environment
conda activate xiaozhi-esp32-server
# Enter your project root directory, then enter main/xiaozhi-server
cd main/xiaozhi-server
pIP config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pIP install -r requirements.txt
```

### 7. Download Speech Recognition Model Files

This project now uses English-supporting ASR services (OpenAI ASR, Groq ASR, etc.) instead of Chinese-focused models. Most ASR services require API keys, while VoskASR requires manual model downloads from https://alphacephei.com/vosk/models (recommended: vosk-model-en-us-0.22 for English).

**For VoskASR (Recommended for English):**

1. **Download the Vosk English Model:**
   - Visit the official Vosk models page: https://alphacephei.com/vosk/models
   - Download the English model: `vosk-model-en-us-0.22.zip` (approximately 1.8 GB)
   - For smaller systems, you can use `vosk-model-small-en-us-0.15.zip` (approximately 40 MB)

2. **Extract the Model:**
   ```bash
   # Navigate to your xiaozhi-server directory
   cd main/xiaozhi-server
   
   # Create a vosk directory inside models
   mkdir -p models/vosk
   
   # Extract the downloaded model to the vosk directory
   # Replace 'vosk-model-en-us-0.22.zip' with the actual filename you downloaded
   unzip vosk-model-en-us-0.22.zip -d models/vosk/
   ```

3. **Verify the Model Structure:**
   After extraction, your directory structure should look like:
   ```
   main/xiaozhi-server
     ├─ data
     ├─ models
        ├─ vosk
           ├─ vosk-model-en-us-0.22
              ├─ am
              ├─ graph
              ├─ ivector
              └─ conf
   ```

4. **Configure the Model Path:**
   In your `.config.yaml` file (located in the `data` folder), set the correct model path:
   ```yaml
   selected_module:
     ASR: VoskASR
   
   ASR:
     VoskASR:
       type: vosk
       model_path: models/vosk/vosk-model-en-us-0.22
       output_dir: tmp/
   ```

## 8. Configure Project Files

Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the first data entry in the list with parameter code `server.secret`, and copy its `Parameter Value`.

`server.secret` needs some explanation. This `Parameter Value` is very important, as it allows our `Server` side to connect to `manager-api`. `server.secret` is a key that is automatically randomly generated each time the manager module is deployed from scratch.

If your `xiaozhi-server` directory doesn't have `data`, you need to create the `data` directory.
If there's no `.config.yaml` file under your `data` directory, you can copy the `config_from_api.yaml` file from the `xiaozhi-server` directory to `data` and rename it to `.config.yaml`

After copying the `Parameter Value`, open the `.config.yaml` file in the `data` directory under `xiaozhi-server`. At this moment, your configuration file content should look like this:

```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: your-server.secret-value
```

Copy the `Parameter Value` of `server.secret` that you just copied from the `Smart Control Panel` into the `secret` field in the `.config.yaml` file.

The result should look like this:
```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

## 9. Run Project

```
# Ensure execution in xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```

If you can see logs similar to the following, it indicates that the project service has started successfully.

```
25-02-23 12:01:09[core.websocket_server] - INFO - Server is running at ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======The above address is a websocket protocol address, please do not access it with a browser=======
25-02-23 12:01:09[core.websocket_server] - INFO - To test websocket, please use Google Chrome to open test_page.html in the test directory
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Since you are deploying all modules, you have two important interfaces.

OTA Interface:
```
http://your-computer-lan-IP:8003/xiaozhi/ota/
```

Websocket Interface:
```
ws://your-computer-lan-IP:8000/xiaozhi/v1/
```

You must write the above two interface addresses into the Smart Control Panel: they will affect websocket address distribution and automatic upgrade functions.

1. Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the parameter code `server.websocket`, and input your `Websocket Interface`.

2. Using the super administrator account, log into the Smart Control Panel, find `Parameter Management` in the top menu, find the parameter code `server.ota`, and input your `OTA Interface`.


Next, you can start operating your ESP32 device. You can either `compile your own ESP32 firmware` or configure to use `Xiage's pre-compiled firmware version 1.6.1 or above`. Choose one of the two options:

1. [Compile your own ESP32 firmware](firmware-build.md).

2. [Configure custom server based on Xiage's pre-compiled firmware](firmware-setting.md).

# Frequently Asked Questions
The following are some common questions for reference:

1. [Why does Xiaozhi recognize multiple languages when I speak?](./FAQ.md)<br/>
2. [Why does the error "TTS task failed: file not found" occur?](./FAQ.md)<br/>
3. [Why does TTS often fail and timeout?](./FAQ.md)<br/>
4. [Why can I connect to the self-built server using WiFi, but not in 4G mode?](./FAQ.md)<br/>
5. [How can I improve Xiaozhi's dialogue response speed?](./FAQ.md)<br/>
6. [Why does Xiaozhi often interrupt when I speak slowly with pauses?](./FAQ.md)<br/>
## Deployment Related Tutorials
1. [How to automatically pull the latest code and compile and start the project](./dev-ops-integration.md)<br/>
2. [How to integrate with Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>
## Extension Related Tutorials
1. [How to enable phone number registration for Smart Control Panel](./ali-sms-integration.md)<br/>
2. [How to integrate with HomeAssistant for smart home control](./homeassistant-integration.md)<br/>
3. [How to enable visual models for photo recognition](./mcp-vision-integration.md)<br/>
4. [How to deploy MCP access points](./mcp-endpoint-enable.md)<br/>
5. [How to integrate with MCP access points](./mcp-endpoint-integration.md)<br/>
6. [How to enable voiceprint recognition](./voiceprint-integration.md)<br/>
8. [Weather plugin usage guide](./weather-integration.md)<br/>
## Voice Cloning and Local Speech Deployment Related Tutorials
## Performance Testing Tutorials
1. [Component speed testing guide](./performance_tester.md)<br/>
2. [Regularly published test results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>
