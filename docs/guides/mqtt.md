# MQTT Gateway Deployment Tutorial

The `xiaozhi-esp32-server` project can be combined with the open-source [xiaozhi-mqtt-gateway](https://github.com/78/xiaozhi-mqtt-gateway) project for simple modification to enable xiaozhi hardware MQTT+UDP connection.

## Preparation

Check the version number at the bottom of your control console homepage to confirm whether your control console version is `0.7.7` or above. If not, you need to upgrade the control console.

Prepare your `mqtt-websocket` connection address for `xiaozhi-server`. Based on your original `websocket address`, add the characters `?from=mqtt_gateway` to get the `mqtt-websocket` connection address.

1. If you are using source code deployment, your `mqtt-websocket` address is:
```
ws://127.0.0.1:8000/xiaozhi/v1?from=mqtt_gateway
```

2. If you are using docker deployment, your `mqtt-websocket` address is
```
ws://your_host_lan_IP:8000/xiaozhi/v1?from=mqtt_gateway
```

## Step 1: Deploy MQTT Gateway

1. Clone the [modified xiaozhi-mqtt-gateway project](https://github.com/lapy/xiaozhi-mqtt-gateway.git):
```bash
git clone https://ghfast.top/https://github.com/lapy/xiaozhi-mqtt-gateway.git
cd xiaozhi-mqtt-gateway
```

2. Install dependencies:
```bash
npm install
npm install -g pm2
```

3. Configure `config.json`:
```bash
cp config/mqtt.json.example config/mqtt.json
```

4. Edit the configuration file config/mqtt.json, replace the `mqtt-websocket` address from the preparation phase into `chat_servers`. For example, the source code deployment of `xiaozhi-server` is configured as follows:

``` 
{
    "production": {
        "chat_servers": [
            "ws://127.0.0.1:8000/xiaozhi/v1?from=mqtt_gateway"
        ]
    },
    "debug": false,
    "max_mqtt_payload_size": 8192,
    "mcp_client": {
        "capabilities": {
        },
        "client_info": {
            "name": "xiaozhi-mqtt-client",
            "version": "1.0.0"
        },
        "max_tools_count": 128
    }
}
```
5. Create a `.env` file in the project root directory and set the following environment variables:
```
PUBLIC_IP=your-IP         # Server public IP
MQTT_PORT=1883            # MQTT server port
UDP_PORT=8884             # UDP server port
API_PORT=8007             # Management API port
MQTT_SIGNATURE_KEY=test   # MQTT signature key
```
Please note the `PUBLIC_IP` configuration, ensure it matches the actual public IP address, or use domain name if available.

`MQTT_SIGNATURE_KEY` is the key used for MQTT connection authentication. It's recommended to set it to something more complex, preferably 8+ characters with both uppercase and lowercase letters. This key will be used later.

- Do not use simple passwords like `123456`, `test`, etc.
- Do not use simple passwords like `123456`, `test`, etc.
- Do not use simple passwords like `123456`, `test`, etc.

6. Start MQTT Gateway
```
# Start service
pm2 start ecosystem.config.js

# View logs
pm2 logs xz-mqtt
```

When you see the following logs, it means the MQTT gateway has started successfully:
```
0|xz-mqtt  | 2025-09-11T12:14:48: MQTT server is listening on port 1883
0|xz-mqtt  | 2025-09-11T12:14:48: UDP server is listening on x.x.x.x:8884
```

If you need to restart the MQTT gateway, execute the following command:
```
pm2 restart xz-mqtt
```

## Step 2: Configure Smart Control Panel

1. At the top of the Smart Control Panel, click `Parameter Management`, search for `server.mqtt_gateway`, click edit, and fill in the `PUBLIC_IP`+`:`+`MQTT_PORT` you set in the `.env` file. Similar to this
```
192.168.0.7:1883
```
2. At the top of the Smart Control Panel, click `Parameter Management`, search for `server.mqtt_signature_key`, click edit, and fill in the `MQTT_SIGNATURE_KEY` you set in the `.env` file.

3. At the top of the Smart Control Panel, click `Parameter Management`, search for `server.udp_gateway`, click edit, and fill in the `PUBLIC_IP`+`:`+`UDP_PORT` you set in the `.env` file. Similar to this
```
192.168.0.7:8884
```
4. At the top of the Smart Control Panel, click `Parameter Management`, search for `server.mqtt_manager_api`, click edit, and fill in the `PUBLIC_IP`+`:`+`UDP_PORT` you set in the `.env` file. Similar to this
```
192.168.0.7:8007
```

After completing the above configuration, you can use the curl command to verify whether your OTA address will distribute MQTT configuration. Change the `http://localhost:8002/xiaozhi/ota/` below to your OTA address
```
curl 'http://localhost:8003/xiaozhi/ota/' \
  -H 'Content-Type: application/json' \
  -H 'Client-Id: 7b94d69a-9808-4c59-9c9b-704333b38aff' \
  -H 'Device-Id: 11:22:33:44:55:66' \
  --data-raw $'{\n  "application": {\n    "version": "1.0.1",\n    "elf_sha256": "1"\n  },\n  "board": {\n    "mac": "11:22:33:44:55:66"\n  }\n}'
```

If the returned content contains `mqtt` related configuration, it means the configuration is successful. Similar to this

```
{"server_time":{"timestamp":1757567894012,"timeZone":"Asia/Shanghai","timezone_offset":480},"activation":{"code":"460609","message":"http://xiaozhi.server.com\n460609","challenge":"11:22:33:44:55:66"},"firmware":{"version":"1.0.1","url":"http://xiaozhi.server.com:8003/xiaozhi/otaMag/download/NOT_ACTIVATED_FIRMWARE_THIS_IS_A_INVALID_URL"},"websocket":{"url":"ws://192.168.4.23:8000/xiaozhi/v1/"},"mqtt":{"endpoint":"192.168.0.7:1883","client_id":"GID_default@@@11_22_33_44_55_66@@@7b94d69a-9808-4c59-9c9b-704333b38aff","username":"eyJpcCI6IjA6MDowOjA6MDowOjA6MSJ9","password":"Y8XP9xcUhVIN9OmbCHT9ETBiYNE3l3Z07Wk46wV9PE8=","publish_topic":"device-server","subscribe_topic":"devices/p2p/11_22_33_44_55_66"}}
```

## Step 3: Restart Xiaozhi Device
Since MQTT information needs to be distributed through the OTA address, you only need to ensure that you can normally connect to the server's OTA address, then restart and wake up.

After waking up, pay attention to the mqtt-gateway logs to confirm if there are successful connection logs.
```
pm2 logs xz-mqtt
```