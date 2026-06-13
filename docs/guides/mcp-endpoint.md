# MCP Endpoint Usage Guide

This tutorial uses the open-source mcp calculator functionality as an example to introduce how to integrate your own custom mcp service into your own endpoint.

The premise of this tutorial is that your `xiaozhi-server` has already enabled the mcp endpoint functionality. If you haven't enabled it yet, you can first enable it according to [this tutorial](./mcp-endpoint-enable.md).

# How to integrate a simple mcp functionality for agents, such as calculator functionality

### If you are using full module deployment
If you are using full module deployment, you can enter the control console, agent management, click `Configure Role`, on the right side of `Intent Recognition`, there is an `Edit Functions` button.

Click this button. In the popup page, at the bottom, there will be `MCP Endpoint`. Normally, it will display the `MCP Endpoint Address` of this agent. Next, let's extend this agent with a calculator functionality based on MCP technology.

This `MCP Endpoint Address` is very important, you will use it later.

### If you are using single module deployment
If you are using single module deployment and you have configured the MCP endpoint address in the configuration file, then normally, when the single module deployment starts, it will output the following logs.
```
250705[__main__]-INFO-Initialize component: vad successful SileroVAD
250705[__main__]-INFO-Initialize component: asr successful OpenaiASR
250705[__main__]-INFO-OTA interface is          http://192.168.1.25:8003/xiaozhi/ota/
250705[__main__]-INFO-Vision analysis interface is     http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp endpoint is        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket address is    ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======The above addresses are websocket protocol addresses, please do not access with browser=======
250705[__main__]-INFO-If you want to test websocket, please open test_page.html in the test directory with Google browser
250705[__main__]-INFO-=============================================================
```

As shown above, the `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc` in the output `mcp endpoint is` is your `MCP Endpoint Address`.

This `MCP endpoint address` is important, you will need it later.

## Step 1: Download the MCP Calculator Project Code

Open the [Calculator Project](https://github.com/78/mcp-calculator) in your browser,

After opening, find the green button that says `Code`, click it, and then you'll see the `Download ZIP` button.

Click it to download the project source code zip file. After downloading to your computer, extract it. At this point, its name might be `mcp-calculator-main`
You need to rename it to `mcp-calculator`. Next, we'll use the command line to enter the project directory and install dependencies


```bash
# Enter project directory
cd mcp-calculator

conda remove -n mcp-calculator --all -y
conda create -n mcp-calculator python=3.10 -y
conda activate mcp-calculator

pIP install -r requirements.txt
```

## Step 2: Start

Before starting, first copy the MCP endpoint address from your smart control panel's agent.

For example, my agent's MCP address is
```
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Start entering commands

```bash
export MCP_ENDPOINT=ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

After entering, start the program

```bash
python mcp_pipe.py calculator.py
```

### If you are using Smart Control Panel deployment
If you are using Smart Control Panel deployment, after starting, go back to the Smart Control Panel and click refresh MCP connection status, and you will see your extended function list.

### If you are using single module deployment
If you are using single module deployment, when the device connects, it will output similar logs, indicating success

```
250705 -INFO-Initializing MCP endpoint: wss://2662r3426b.vicp.fun/mcp_e 
250705 -INFO-Sending MCP endpoint initialization message
250705 -INFO-MCP endpoint connection successful
250705 -INFO-MCP endpoint initialization successful
250705 -INFO-Unified tool processor initialization complete
250705 -INFO-MCP endpoint server info: name=Calculator, version=1.9.4
250705 -INFO-MCP endpoint supported tools count: 1
250705 -INFO-All MCP endpoint tools obtained, client ready
250705 -INFO-Tool cache refreshed
250705 -INFO-Current supported function list: [ 'get_time', 'get_calendar', 'play_music', 'get_weather', 'handle_exit_intent', 'calculator']
```
If it includes `'calculator'`, it means the device can call the calculator tool based on intent recognition.