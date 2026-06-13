# Xiaozhi ESP32 Open Source Server and HomeAssistant Integration Guide

[TOC]

-----

## Introduction

This document will guide you on how to integrate ESP32 devices with HomeAssistant.

## Prerequisites

- HomeAssistant is installed and configured
- The model I chose this time is: free OpenAI, which supports function call

## Pre-start Operations (Required)

### 1. Get HA Network Address Information

Please visit your Home Assistant network address. For example, my HA address is 192.168.4.7, and the port is the default 8123, then open in the browser

```
http://192.168.4.7:8123
```

> Manual method to query HA's IP address**（Only applicable when xiaozhi-esp32-server and HA are deployed on the same network device [e.g., same wifi]）**：
>
> 1. Enter Home Assistant (frontend).
>
> 2. Click **Settings** in the bottom left corner → **System** → **Network**.
>
> 3. Scroll to the bottom `Home Assistant website` area, in `local network`, click the `eye` button to see the currently used IP address (such as `192.168.1.10`) and network interface. Click `copy link` to copy directly.

Alternatively, if you have set up a directly accessible Home Assistant OAuth address, you can also access it directly in the browser

```
http://homeassistant.local:8123
```

### 2. Login to `Home Assistant` to get development key

Login to `HomeAssistant`, click `bottom left avatar -> Profile`, switch to `Security` navigation bar, scroll to the bottom `Long-lived access tokens` to generate api_key, and copy and save it. All subsequent methods require this api key and it only appears once (tIP: you can save the generated QR code image, and scan the QR code later to extract the api key again).

## Method 1: Xiaozhi Community-built HA Calling Function

### Function DescrIPtion

- If you need to add new devices later, this method requires manually restarting the `xiaozhi-esp32-server service` to update device information**（Important**).

- You need to ensure that `Xiaomi Home` has been integrated in HomeAssistant and Mi Home devices have been imported into `HomeAssistant`.

- You need to ensure that the `xiaozhi-esp32-server Smart Control Console` can be used normally.

- My `xiaozhi-esp32-server Smart Control Console` and `HomeAssistant` are deployed on the same machine on another port, version is `0.3.10`

  ```
  http://192.168.4.7:8002
  ```


### Configuration Steps

#### 1. Login to `HomeAssistant` to organize the device list that needs to be controlled

Login to `HomeAssistant`, click `Settings in the bottom left corner`, then enter `Devices & Services`, and click `Entities` at the top.

Then search for the switches you want to control in entities. After the results appear, click on one of the results in the list, and a switch interface will appear.

In the switch interface, we try clicking the switch to see if it turns on/off with our clicks. If it can be operated, it means it's properly connected to the network.

Then find the settings button in the switch panel, click it, and you can view the `Entity ID` of this switch.

We open a notepad and organize a piece of data in this format:

Location + English comma + Device name + English comma + `Entity ID` + English semicolon

For example, I'm at the company, I have a toy light, its identifier is switch.cuco_cn_460494544_cp1_on_p_2_1, then write this piece of data:

```
Company,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;
```

Of course, in the end I might need to operate two lights, my final result is:

```
Company,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;
Company,Desk Lamp,switch.iot_cn_831898993_socn1_on_p_2_1;
```

This string, we call it "device list string" and need to save it well, it will be useful later.

#### 2. Login to `Smart Control Console`

Use the administrator account to login to the `Smart Control Console`. In `Agent Management`, find your agent, then click `Configure Role`.

Set intent recognition to `Function Call` or `LLM Intent Recognition`. At this time you will see an `Edit Functions` button on the right. Click the `Edit Functions` button, and a `Function Management` dialog will pop up.

In the `Function Management` dialog, you need to check `HomeAssistant Device Status Query` and `HomeAssistant Device Status Modification`.

After checking, click `HomeAssistant Device Status Query` in `Selected Functions`, then configure your `HomeAssistant` address, key, and device list string in `Parameter Configuration`.

After editing, click `Save Configuration`, then the `Function Management` dialog will be hidden, then click save agent configuration.

After successful saving, you can wake up the device for operation.

#### 3. Wake up device for control

Try saying to the esp32, "Turn on XXX light"

## Method 2: Xiaozhi uses Home Assistant's voice assistant as LLM tool

### Function DescrIPtion

- This method has a relatively serious disadvantage——**This method cannot use the function_call plugin capabilities of the Xiaozhi open source ecosystem**, because using Home Assistant as Xiaozhi's LLM tool will transfer the intent recognition capability to Home Assistant. However, **this method can experience the native Home Assistant operation functions, and Xiaozhi's chat capability remains unchanged**. If you are really concerned, you can use [Method 3](##Method 3: Using Home Assistant's MCP service (recommended)) which is also supported by Home Assistant, which can maximize the experience of Home Assistant's functions.

### Configuration Steps:

#### 1. Configure Home Assistant's large model voice assistant.

**You need to configure Home Assistant's voice assistant or large model tool in advance.**

#### 2. Get Home Assistant's voice assistant Agent ID.

1. Enter the Home Assistant page. Click `Developer Tools` on the left.
2. In the opened `Developer Tools`, click the `Actions` tab (as shown in operation 1), in the `Actions` option bar on the page, find or enter `conversation.process (conversation-process)` and select `Conversation: Process` (as shown in operation 2).

3. Check the `Agent` option on the page, in the highlighted `Conversation Agent`, select the voice assistant name you configured in step 1, as shown in the figure, I have configured `OpenAI` and select it.

4. After selection, click `Enter YAML mode` at the bottom left of the form.

5. Copy the agent-id value, for example, mine in the figure is `01JP2DYMBDF7F4ZA2DMCF2AGX2` (for reference only).

6. Switch to the `config.yaml` file of the Xiaozhi open source server `xiaozhi-esp32-server`, in the LLM configuration, find Home Assistant, set your Home Assistant network address, Api key and the agent_id you just queried.
7. Modify the `LLM` of the `selected_module` attribute in the `config.yaml` file to `HomeAssistant`, and `Intent` to `nointent`.
8. Restart the Xiaozhi open source server `xiaozhi-esp32-server` to use it normally.

## Method 3: Using Home Assistant's MCP service (recommended)

### Function DescrIPtion

- You need to integrate and install the HA integration in Home Assistant in advance——[Model Context Protocol Server](https://www.home-assistant.io/integrations/mcp_server/).

- This method and Method 2 are both solutions provided by HA officially. Unlike Method 2, you can normally use the open source community-built plugins of the Xiaozhi open source server `xiaozhi-esp32-server`, while allowing you to freely use any LLM large model that supports function_call functionality.

### Configuration Steps

#### 1. Install Home Assistant's MCP service integration.

Official integration website——[Model Context Protocol Server](https://www.home-assistant.io/integrations/mcp_server/)..

Or follow the manual operations below.

> - Go to Home Assistant page **[Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations)**.
>
> - In the bottom right corner, select the **[Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=mcp_server)** button.
>
> - Select **Model Context Protocol Server** from the list.
>
> - Follow the on-screen instructions to complete the setup.

#### 2. Configure Xiaozhi open source server MCP configuration information

Enter the `data` directory and find the `.mcp_server_settings.json` file.

If you don't have a `.mcp_server_settings.json` file in your `data` directory,
- Please copy the `mcp_server_settings.json` file from the root directory of the `xiaozhi-server` folder to the `data` directory and rename it to `.mcp_server_settings.json`
- Or [download this file](https://github.com/lapy/xiaozhi-esp32-server/blob/main/main/xiaozhi-server/mcp_server_settings.json), download it to the `data` directory and rename it to `.mcp_server_settings.json`

Modify this part of the content in `"mcpServers"`:

```json
"Home Assistant": {
      "command": "mcp-proxy",
      "args": [
        "http://YOUR_HA_HOST/mcp_server/sse"
      ],
      "env": {
        "API_ACCESS_TOKEN": "YOUR_API_ACCESS_TOKEN"
      }
},
```

Note:

1. **Replace configuration:**
   - Replace `YOUR_HA_HOST` in `args` with your HA service address. If your service address already contains https/http (e.g., `http://192.168.1.101:8123`), just fill in `192.168.1.101:8123`.
   - Replace `YOUR_API_ACCESS_TOKEN` in `API_ACCESS_TOKEN` in `env` with the development key api key you obtained earlier.
2. **If you add configuration and there are no new `mcpServers` configurations after the `"mcpServers"` brackets, you need to remove the final comma `,`**, otherwise parsing may fail.

**Final effect reference (as follows)**:

```json
 "mcpServers": {
    "Home Assistant": {
      "command": "mcp-proxy",
      "args": [
        "http://192.168.1.101:8123/mcp_server/sse"
      ],
      "env": {
        "API_ACCESS_TOKEN": "abcd.efghi.jkl"
      }
    }
  }
```

#### 3. Configure Xiaozhi open source server system configuration

1. **Select any LLM large model that supports function_call as Xiaozhi's LLM chat assistant (but don't select Home Assistant as LLM tool)**. The model I chose this time is: free OpenAI, which supports functioncall function calling, but sometimes the calls are not very stable. If you want to pursue stability, it is recommended to set LLM to: OpenAILLM, using the specific model_name: gpt-4o-mini.

2. Switch to the `config.yaml` file of the Xiaozhi open source server `xiaozhi-esp32-server`, set your LLM large model configuration, and adjust the `Intent` of the `selected_module` configuration to `function_call`.

3. Restart the Xiaozhi open source server `xiaozhi-esp32-server` to use it normally.