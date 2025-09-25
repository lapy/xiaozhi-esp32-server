# Voiceprint Recognition Enablement Guide

This tutorial contains 3 parts
- 1. How to deploy voiceprint recognition service
- 2. How to configure voiceprint recognition interface in full module deployment
- 3. How to configure voiceprint recognition in minimal deployment

# 1. How to Deploy Voiceprint Recognition Service

## Step 1: Download Voiceprint Recognition Project Source Code

Open [Voiceprint Recognition Project Address](https://github.com/xinnan-tech/voiceprint-api) in browser

After opening, find a green button on the page that says `Code`, click it, then you will see the `Download ZIP` button.

Click it to download the project source code zIP package. After downloading to your computer, extract it, and its name might be `voiceprint-api-main`
You need to rename it to `voiceprint-api`.

## Step 2: Create Database and Tables

Voiceprint recognition depends on `mysql` database. If you have already deployed `Smart Control Panel`, it means you have already installed `mysql`. You can share it.

You can try using the `telnet` command on the host machine to see if you can normally access the `3306` port of `mysql`.
```
telnet 127.0.0.1 3306
```
If you can access port 3306, please ignore the following content and go directly to step 3.

If you cannot access it, you need to recall how your `mysql` was installed.

If your mysql was installed using an installation package by yourself, it means your `mysql` has network isolation. You may need to solve the problem of accessing the `3306` port of `mysql` first.

If your `mysql` was installed through this project's `docker-compose_all.yml`. You need to find the `docker-compose_all.yml` file you used to create the database at that time and modify the following content

Before modification
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
```

After modification
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
```

Note that change `expose` under `xiaozhi-esp32-server-db` to `ports`. After modification, you need to restart. The following are the commands to restart mysql:

```
# Enter the folder where your docker-compose_all.yml is located, for example mine is xiaozhi-server
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

After startup, use the `telnet` command again on the host machine to see if you can normally access the `3306` port of `mysql`.
```
telnet 127.0.0.1 3306
```
Normally this should allow access.

## Step 3: Create Database and Tables
If your host machine can normally access the mysql database, then create a database named `voiceprint_db` and a `voiceprints` table on mysql.

```
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Step 4: Configure Database Connection

Enter the `voiceprint-api` folder and create a folder named `data`.

Copy `voiceprint.yaml` from the root directory of `voiceprint-api` to the `data` folder and rename it to `.voiceprint.yaml`

Next, you need to focus on configuring the database connection in `.voiceprint.yaml`.

```
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled with the `local area network IP of the machine where mysql is located`.

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled with the `local area network IP of the machine where mysql is located`.

Note! Since your voiceprint recognition service is deployed using docker, `host` needs to be filled with the `local area network IP of the machine where mysql is located`.

## Step 5: Start Program
This project is a very simple project, it is recommended to use docker to run. However, if you don't want to use docker to run, you can refer to [this page](https://github.com/xinnan-tech/voiceprint-api/blob/main/README.md) to run with source code. The following is the docker running method

```
# Enter the root directory of this project source code
cd voiceprint-api

# Clear cache
docker compose -f docker-compose.yml down
docker stop voiceprint-api
docker rm voiceprint-api
docker rmi ghcr.nju.edu.cn/xinnan-tech/voiceprint-api:latest

# Start docker container
docker compose -f docker-compose.yml up -d
# View logs
docker logs -f voiceprint-api
```

At this time, the logs will output logs similar to the following
```
250711 INFO-🚀 Start: Production environment service startup (Uvicorn), listening address: 0.0.0.0:8005
250711 INFO-============================================================
250711 INFO-Voiceprint interface address: http://127.0.0.1:8005/voiceprint/health?key=abcd
250711 INFO-============================================================
```

Please copy out the voiceprint interface address:

Since you are using docker deployment, do not use the above address directly!

Since you are using docker deployment, do not use the above address directly!

Since you are using docker deployment, do not use the above address directly!

First copy out the address and put it in a draft, you need to know what your computer's local area network IP is, for example my computer's local area network IP is `192.168.1.25`, then
My original interface address
```
http://127.0.0.1:8005/voiceprint/health?key=abcd

```
should be changed to
```
http://192.168.1.25:8005/voiceprint/health?key=abcd
```

After modification, please use a browser to directly access the `voiceprint interface address`. When the browser shows code similar to this, it means it is successful.
```
{"total_voiceprints":0,"status":"healthy"}
```

Please keep the `voiceprint interface address` after modification, it will be needed in the next step.

# 2. How to Configure Voiceprint Recognition in Full Module Deployment

## Step 1: Configure Interface
If you are doing full module deployment, use an administrator account, login to the Smart Control Panel, click the top `Parameter Dictionary`, and select the `Parameter Management` function.

Then search for the parameter `server.voice_print`, at this time, its value should be `null`.
Click the modify button, paste the `voiceprint interface address` obtained from the previous step into the `parameter value`. Then save.

If it can be saved successfully, it means everything is going well, you can go to the agent to check the effect. If it is not successful, it means the Smart Control Panel cannot access voiceprint recognition, most likely due to network firewall or not filling in the correct local area network IP.

## Step 2: Set Agent Memory Mode

Enter your agent's role configuration, set the memory to `Local Short-term Memory`, and be sure to enable `Report Text + Voice`.

## Step 3: Chat with Your Agent

Power on your device, then chat with it using normal speech rate and tone.

## Step 4: Set Voiceprint

In the Smart Control Panel, on the `Agent Management` page, in the agent panel, there is a `Voiceprint Recognition` button, click it. At the bottom there is an `Add` button. You can register voiceprints for what someone says.
In the popup box, the `descrIPtion` attribute is recommended to be filled in, which can be the person's profession, personality, hobbies. This facilitates the agent's analysis and understanding of the speaker.

## Step 3: Chat with Your Agent

Power on your device and ask it, do you know who I am? If it can answer correctly, it means the voiceprint recognition function is working normally.

# 3. How to Configure Voiceprint Recognition in Minimal Deployment

## Step 1: Configure Interface
Open the `xiaozhi-server/data/.config.yaml` file (create if it doesn't exist), then add/modify the following content:

```
# Voiceprint recognition configuration
voiceprint:
  # Voiceprint interface address
  url: Your voiceprint interface address
  # Speaker configuration: speaker_id,name,descrIPtion
  speakers:
    - "test1,Zhang San,Zhang San is a programmer"
    - "test2,Li Si,Li Si is a product manager"
    - "test3,Wang Wu,Wang Wu is a designer"
```

Paste the `voiceprint interface address` obtained from the previous step into `url`. Then save.

Add `speakers` parameters according to requirements. Note that this `speaker_id` parameter will be used later for voiceprint registration.

## Step 2: Register Voiceprint
If you have already started the voiceprint service, you can access `http://localhost:8005/voiceprint/docs` in your local browser to view the API documentation. Here we only explain how to use the voiceprint registration API.

The voiceprint registration API address is `http://localhost:8005/voiceprint/register`, and the request method is POST.

The request header needs to include Bearer Token authentication, where the token is the part after `?key=` in the `voiceprint interface address`. For example, if my voiceprint registration address is `http://127.0.0.1:8005/voiceprint/health?key=abcd`, then my token is `abcd`.

The request body contains speaker ID (speaker_id) and WAV audio file (file). The request example is as follows:

```
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "speaker_id=your_speaker_id_here" \
  -F "file=@/path/to/your/file" \
  http://localhost:8005/voiceprint/register
```

 Here `file` is the audio file of the speaker to be registered, and `speaker_id` needs to be consistent with the `speaker_id` configured in step 1. For example, if I need to register Zhang San's voiceprint, and Zhang San's `speaker_id` filled in `.config.yaml` is `test1`, then when I register Zhang San's voiceprint, the `speaker_id` filled in the request body is `test1`, and `file` is filled with the audio file of Zhang San speaking a paragraph.

 ## Step 3: Start Service

Start the Xiaozhi server and voiceprint service, and you can use it normally.
