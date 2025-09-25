# Configure Custom Server Based on Pre-compiled Firmware

## Step 1: Confirm Version
Flash the pre-compiled [firmware version 1.6.1 or above](https://github.com/78/xiaozhi-esp32/releases)

## Step 2: Prepare Your OTA Address
If you followed the tutorial and used full module deployment, you should have an OTA address.

Now, please open your OTA address in a browser, for example my OTA address:
```
https://2662r3426b.vicp.fun/xiaozhi/ota/
```

If it shows "OTA interface running normally, websocket cluster count: X", then proceed.

If it shows "OTA interface not running normally", it's probably because you haven't configured the `Websocket` address in the `Control Panel`. Then:

- 1. Log in to the Control Panel as super administrator

- 2. Click `Parameter Management` in the top menu

- 3. Find the `server.websocket` item in the list and enter your `Websocket` address. For example, mine is:

```
wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

After configuration, refresh your OTA interface address in the browser to see if it's working normally. If it's still not working, confirm again whether WebSocket is running normally and whether the WebSocket address is configured.

## Step 3: Enter Network Configuration Mode
Enter the machine's network configuration mode, click "Advanced Options" at the top of the page, enter your server's `OTA` address, and click Save. Restart the device.
![Please refer to - OTA Address Settings](../docs/images/firmware-setting-ota.png)

## Step 4: Wake up Xiaozhi and Check Log Output

Wake up Xiaozhi and see if the logs are outputting normally.

## Common Issues
The following are some common issues for reference:

[1. Why does Xiaozhi recognize many Korean, Japanese, and English words when I speak?](./FAQ.md)

[2. Why does the error "TTS task failed: file not found" occur?](./FAQ.md)

[3. TTS often fails and times out](./FAQ.md)

[4. Can connect to self-built server using WiFi, but 4G mode cannot connect](./FAQ.md)

[5. How to improve Xiaozhi's conversation response speed?](./FAQ.md)

[6. I speak slowly, and Xiaozhi keeps interrupting during pauses](./FAQ.md)

[7. I want to control lights, air conditioning, remote power on/off, etc. through Xiaozhi](./FAQ.md)
