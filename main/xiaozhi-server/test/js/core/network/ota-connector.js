import { log } from '../../utils/logger.js?v=0205';

// WebSocket connection bootstrap.
export async function webSocketConnect(otaUrl, config) {

    if (!validateConfig(config)) {
        return;
    }

    // Send the OTA request and read the returned WebSocket details.
    const otaResult = await sendOTA(otaUrl, config);
    if (!otaResult) {
        log('Could not retrieve connection details from the OTA server.', 'error');
        return;
    }

    // Extract the WebSocket details from the OTA response.
    const { websocket } = otaResult;
    if (!websocket || !websocket.url) {
        log('The OTA response does not include WebSocket information.', 'error');
        return;
    }

    // Start from the WebSocket URL returned by the OTA endpoint.
    let connUrl = new URL(websocket.url);

    // Forward the token returned by the OTA response.
    if (websocket.token) {
        if (websocket.token.startsWith("Bearer ")) {
            connUrl.searchParams.append('authorization', websocket.token);
        } else {
            connUrl.searchParams.append('authorization', 'Bearer ' + websocket.token);
        }
    }

    // Preserve the existing device/client query parameters.
    connUrl.searchParams.append('device-id', config.deviceId);
    connUrl.searchParams.append('client-id', config.clientId);

    const wsurl = connUrl.toString()

    log(`Connecting to: ${wsurl}`, 'info');

    if (wsurl) {
        document.getElementById('serverUrl').value = wsurl;
    }

    return new WebSocket(connUrl.toString());
}

// Validate the required configuration fields.
function validateConfig(config) {
    if (!config.deviceMac) {
        log('Device MAC address is required.', 'error');
        return false;
    }
    if (!config.clientId) {
        log('Client ID is required.', 'error');
        return false;
    }
    return true;
}

// Send the OTA request and return the parsed response.
async function sendOTA(otaUrl, config) {
    try {
        const res = await fetch(otaUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Device-Id': config.deviceId,
                'Client-Id': config.clientId
            },
            body: JSON.stringify({
                version: 0,
                uuid: '',
                application: {
                    name: 'xiaozhi-web-test',
                    version: '1.0.0',
                    compile_time: '2025-04-16 10:00:00',
                    idf_version: '4.4.3',
                    elf_sha256: '1234567890abcdef1234567890abcdef1234567890abcdef'
                },
                ota: { label: 'xiaozhi-web-test' },
                board: {
                    type: config.deviceName,
                    ssid: 'xiaozhi-web-test',
                    rssi: 0,
                    channel: 0,
                    ip: '192.168.1.1',
                    mac: config.deviceMac
                },
                flash_size: 0,
                minimum_free_heap_size: 0,
                mac_address: config.deviceMac,
                chip_model_name: '',
                chip_info: { model: 0, cores: 0, revision: 0, features: 0 },
                partition_table: [{ label: '', type: 0, subtype: 0, address: 0, size: 0 }]
            })
        });

        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

        const result = await res.json();
        return result; // Return the full response payload.
    } catch (err) {
        return null; // Return null on failure.
    }
}
