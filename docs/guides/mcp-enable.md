# MCP Endpoint Deployment Usage Guide

This tutorial contains 3 parts
- 1. How to deploy the MCP endpoint service
- 2. How to configure MCP endpoint when deploying all modules
- 3. How to configure MCP endpoint when deploying single module

# 1. How to Deploy MCP Endpoint Service

## Step 1: Download MCP Endpoint Project Source Code

Open [MCP Endpoint Project Address](https://github.com/lapy/mcp-endpoint-server) in browser

After opening, find a green button on the page that says `Code`, click it, and then you'll see the `Download ZIP` button.

Click it to download the project source code archive. After downloading to your computer, extract it. At this time, its name might be `mcp-endpoint-server-main`
You need to rename it to `mcp-endpoint-server`.

## Step 2: Start the Program
This project is a very simple project, it is recommended to use docker to run. However, if you don't want to use docker to run, you can refer to [this page](https://github.com/lapy/mcp-endpoint-server/blob/main/README_dev.md) to run with source code. The following is the docker running method

```
# Enter the root directory of this project source code
cd mcp-endpoint-server

# Clear cache
docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server
docker rm mcp-endpoint-server
docker rmi ghcr.io/lapy/mcp-endpoint-server:latest

# Start docker container
docker compose -f docker-compose.yml up -d
# View logs
docker logs -f mcp-endpoint-server
```

At this point, the logs will output similar logs as follows
```
250705 INFO-=====The following addresses are Smart Control Panel/Single Module MCP endpoint addresses====
250705 INFO-Smart Control Panel MCP parameter configuration: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-Single module deployment MCP endpoint: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-=====Please choose according to specific deployment, do not leak to anyone======
```

Please copy out the two interface addresses:

Since you are using docker deployment, you must not use the above addresses directly!


First copy out the addresses and put them in a draft. You need to know what your computer's local network IP is. For example, my computer's local network IP is `192.168.1.25`, then
My original interface addresses
```
Smart Control Panel MCP parameter configuration: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
Single module deployment MCP endpoint: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
```
Should be changed to
```
Smart Control Panel MCP parameter configuration: http://192.168.1.25:8004/mcp_endpoint/health?key=abc
Single module deployment MCP endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

After making the changes, please use your browser to directly access the `Smart Control Panel MCP parameter configuration`. When the browser shows similar code like this, it means it's successful.
```
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

Please keep the above two `interface addresses` safe, you will need them in the next step.

# 2. How to configure MCP endpoint for full module deployment

If you are using full module deployment, use the administrator account to log in to the Smart Control Panel, click the top `Parameter Dictionary`, and select the `Parameter Management` function.

Then search for the parameter `server.mcp_endpoint`. At this point, its value should be `null`.
Click the modify button and paste the `Smart Control Panel MCP parameter configuration` obtained from the previous step into the `Parameter Value`. Then save.

If it can be saved successfully, it means everything is going well, and you can go to the agent to see the effect. If it's not successful, it means the Smart Control Panel cannot access the MCP endpoint, most likely due to network firewall or not filling in the correct local network IP.

# 3. How to configure MCP endpoint for single module deployment

If you are using single module deployment, find your configuration file `data/.config.yaml`.
Search for `mcp_endpoint` in the configuration file. If not found, add the `mcp_endpoint` configuration. Similar to mine like this
```
server:
  websocket: ws://your_IP_or_domain:port_number/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# There may be more configurations here..

mcp_endpoint: your_endpoint_websocket_address
```
At this point, please paste the `Single module deployment MCP endpoint` obtained from `How to deploy MCP endpoint service` into `mcp_endpoint`. Similar to this

```
server:
  websocket: ws://your_IP_or_domain:port_number/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# There may be more configurations here

mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

After configuration, starting the single module will output the following logs.
```
250705[__main__]-INFO-Component initialization: vad successful SileroVAD
250705[__main__]-INFO-Component initialization: asr successful OpenaiASR
250705[__main__]-INFO-OTA interface is          http://192.168.1.25:8003/xiaozhi/ota/
250705[__main__]-INFO-Vision analysis interface is     http://192.168.1.25:8003/mcp/vision/explain
250705[__main__]-INFO-MCP endpoint is        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket address is    ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======The above addresses are websocket protocol addresses, do not access with browser=======
250705[__main__]-INFO-If you want to test websocket, please use Google Chrome to open test_page.html in the test directory
250705[__main__]-INFO-=============================================================
```

As above, if you can output similar `MCP endpoint is` with `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc`, it means the configuration is successful.

