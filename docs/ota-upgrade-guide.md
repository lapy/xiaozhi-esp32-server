# OTA Firmware Upgrade Guide for Single-Module Deployments

This guide explains how to configure automatic OTA firmware upgrades when you are running the single-module `xiaozhi-server` deployment.

If you are using the full-module deployment, you can skip this guide.

## Overview

In single-module mode, `xiaozhi-server` includes built-in OTA firmware management. It can check device versions, match the correct firmware for the device model, and serve updated firmware automatically.

## Prerequisites

- You already have a working single-module deployment of `xiaozhi-server`
- Your device can connect to the server successfully

## Step 1: Prepare the firmware file

### 1. Create the firmware directory

Firmware files must be placed in `data/bin/`. Create it if it does not already exist:

```bash
mkdir -p data/bin
```

### 2. Follow the required filename format

Firmware files must follow this format:

```text
{device_model}_{version}.bin
```

Rules:

- `device_model`: the device model name, for example `lichuang-dev` or `bread-compact-wifi`
- `version`: must begin with a number and may contain letters, dots, underscores, and hyphens
- the file extension must be `.bin`

Examples:

```text
bread-compact-wifi_1.6.6.bin
lichuang-dev_2.0.0.bin
```

### 3. Copy the correct firmware artifact

Copy the OTA upgrade artifact into `data/bin/`:

Important: use `xiaozhi.bin`, not the full firmware image `merged-binary.bin`.

```bash
cp xiaozhi.bin data/bin/device_model_version.bin
```

Example:

```bash
cp xiaozhi.bin data/bin/bread-compact-wifi_1.6.6.bin
```

## Step 2: Configure the public access address

This step is required only for public internet deployments.

If your `xiaozhi-server` instance is exposed through a public IP or domain, you must configure `server.vision_explain` because the OTA download URL is derived from that address.

If your deployment is LAN-only, you can skip this step.

### Why this is required

When `xiaozhi-server` builds OTA download URLs, it uses the host and port from the `vision_explain` setting. If that value is missing or incorrect, devices will not be able to download firmware updates.

### How to configure it

Open `data/.config.yaml`, find the `server` section, and set `vision_explain`:

```yaml
server:
  vision_explain: http://your-domain-or-ip:8003/mcp/vision/explain
```

Examples:

LAN deployment:

```yaml
server:
  vision_explain: http://192.168.1.100:8003/mcp/vision/explain
```

Public domain deployment:

```yaml
server:
  vision_explain: http://yourdomain.com:8003/mcp/vision/explain
```

### Notes

- The domain or IP must be reachable by the device
- If you use Docker, do not use internal-only addresses such as `127.0.0.1` or `localhost`
- If you use `nginx` as a reverse proxy, enter the externally reachable host and port, not the internal service port

## Troubleshooting

### 1. The device does not receive an update

Check the following:

- the firmware file name matches `{model}_{version}.bin`
- the firmware file is in `data/bin/`
- the device model matches the model segment in the file name
- the firmware version is newer than the current device version
- the server logs show OTA requests being handled

### 2. The device cannot reach the download URL

Check the following:

- `server.vision_explain` points to the correct public host or IP
- the configured port is correct, usually `8003`
- the device can reach that public address
- you are not using a Docker-internal address such as `127.0.0.1`
- the firewall allows the required port
- if you use `nginx`, you entered the public host and port rather than the internal app port

### 3. How to confirm the device's current version

Look at the OTA request logs. They include the version reported by the device:

```text
[ota_handler] - Device AA:BB:CC:DD:EE:FF firmware is already up to date: 1.6.6
```

### 4. The new firmware file is not detected immediately

There is a cache window of 30 seconds by default. You can:

- wait 30 seconds and try the OTA request again
- restart the `xiaozhi-server` service
- reduce the `firmware_cache_ttl` setting if you want faster refreshes
