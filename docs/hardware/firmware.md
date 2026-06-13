# ESP32 Firmware Compilation

## Step 1: Prepare Your OTA Address

If you are using version 0.3.12 of this project, whether it's simple Server deployment or full module deployment, you will have an OTA address.

Since the OTA address setup method for simple Server deployment and full module deployment is different, please choose the specific method below:

### If you are using Simple Server Deployment
At this time, please open your OTA address with a browser, for example my OTA address
```
http://192.168.1.25:8003/xiaozhi/ota/
```
If it displays "OTA interface is running normally, the websocket address sent to the device is: ws://xxx:8000/xiaozhi/v1/

You can use the project's built-in `test_page.html` to test whether you can connect to the websocket address output by the OTA page.

If you can't access it, you need to modify the `server.websocket` address in the configuration file `.config.yaml`, restart and test again until `test_page.html` can access normally.

After success, please proceed to Step 2

### If you are using Full Module Deployment
At this time, please open your OTA address with a browser, for example my OTA address
```
http://192.168.1.25:8003/xiaozhi/ota/
```

If it displays "OTA interface is running normally, websocket cluster count: X". Then proceed to step 2.

If it displays "OTA interface is not running normally", you probably haven't configured the `Websocket` address in the `Control Console`. Then:

- 1. Use super administrator to login to the control console

- 2. Click `Parameter Management` in the top menu

- 3. Find the `server.websocket` item in the list and enter your `Websocket` address. For example, mine is

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

After configuration, refresh your OTA interface address with a browser to see if it's normal. If it's still not normal, confirm again whether Websocket is started normally and whether the Websocket address is configured.

## Step 2: Configure Environment
First configure the project environment according to this tutorial [Windows ESP IDF 5.3.2 Development Environment Setup and Xiaozhi Compilation](https://github.com/lapy/xiaozhi-esp32-server/wiki)

## Step 3: Open Configuration File
After configuring the compilation environment, download the xiaozhi-esp32 project source code,

Download the xiaozhi-esp32 project source code from here: [xiaozhi-esp32 project source code](https://github.com/78/xiaozhi-esp32).

After downloading, open the `xiaozhi-esp32/main/Kconfig.projbuild` file.

## Step 4: Modify OTA Address

Find the content of `default` for `OTA_URL`, change `https://api.tenclass.net/xiaozhi/ota/`
   to your own address. For example, if my interface address is `http://192.168.1.25:8003/xiaozhi/ota/`, change the content to this.

Before modification:
```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```
After modification:
```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8003/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

## Step 4: Set Compilation Parameters

Set compilation parameters

```
# Enter the xiaozhi-esp32 root directory from terminal command line
cd xiaozhi-esp32
# For example, I use esp32s3 board, so set compilation target to esp32s3. If your board is other model, please replace with corresponding model
idf.py set-target esp32s3
# Enter menu configuration
idf.py menuconfig
```

After entering menu configuration, go to `Xiaozhi Assistant` and set `BOARD_TYPE` to your board's specific model
Save and exit, return to terminal command line.

## Step 5: Compile Firmware

```
idf.py build
```

## Step 6: Package bin Firmware

```
cd scrIPts
python release.py
```

After the above packaging command is executed, the firmware file `merged-binary.bin` will be generated in the `build` directory under the project root directory.
This `merged-binary.bin` is the firmware file to be burned to the hardware.

Note: If you encounter a "zIP" related error after executing the second command, please ignore this error. As long as the firmware file `merged-binary.bin` is generated in the `build` directory, it won't have much impact on you, please continue.

## Step 7: Burn Firmware
   Connect the ESP32 device to your computer, use Chrome browser to open the following URL

```
https://espressif.github.io/esp-launchpad/
```

Open this tutorial, [Flash Tool/Web-based Firmware Burning (No IDF Development Environment)](https://github.com/lapy/xiaozhi-esp32-server/wiki).
Go to: `Method 2: ESP-Launchpad Browser WEB-based Burning`, starting from `3. Burn Firmware/Download to Development Board`, follow the tutorial.

After successful burning and network connection, wake up Xiaozhi through the wake word and pay attention to the console information output by the server.

## Common Issues
The following are some common issues for reference:

[1. Why does Xiaozhi recognize many Korean, Japanese, and English words when I speak?](../support/faq.md)

[2. Why does "TTS task error file does not exist" occur?](../support/faq.md)

[3. TTS often fails and times out](../support/faq.md)

[4. Can connect to self-built server using WiFi, but cannot connect in 4G mode](../support/faq.md)

[5. How to improve Xiaozhi's conversation response speed?](../support/faq.md)

[6. I speak slowly, and Xiaozhi keeps interrupting when I pause](../support/faq.md)

[7. I want to control lights, air conditioning, remote power on/off and other operations through Xiaozhi](../support/faq.md)
