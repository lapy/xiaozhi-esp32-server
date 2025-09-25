import { log } from './utils/logger.js';
import { otaStatusStyle } from './document.js'

// WebSocket connection
export async function webSocketConnect(otaUrl,wsUrl,config){
    if (!validateWsUrl(wsUrl)) {
        return;          // Return directly, no further execution
    }

    if (!validateConfig(config)) {
        return;
    }
    const ok = await sendOTA(otaUrl, config);
    if (!ok) return;

    // Use custom WebSocket implementation to add authentication header information
    let connUrl = new URL(wsUrl);
    // Add authentication parameters
    connUrl.searchParams.append('device-id', config.deviceId);
    connUrl.searchParams.append('client-id', config.clientId);
    log(`Connecting: ${connUrl.toString()}`, 'info');

    return new WebSocket(connUrl.toString());
}

// Validate configuration
function validateConfig(config) {
    if (!config.deviceMac) {
        log('Device MAC address cannot be empty', 'error');
        return false;
    }
    if (!config.clientId) {
        log('Client ID cannot be empty', 'error');
        return false;
    }
    return true;
}

// Check if wsUrl path has errors
function validateWsUrl(wsUrl){
    if (wsUrl === '') return false;
    // Check URL format
    if (!wsUrl.startsWith('ws://') && !wsUrl.startsWith('wss://')) {
        log('URL format error, must start with ws:// or wss://', 'error');
        return false;
    }
    return true
}


// Send OTA request, verify status
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
                    type: 'xiaozhi-web-test',
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
        otaStatusStyle(true)
        return true; // Success
    } catch (err) {
        otaStatusStyle(false)
        return false; // Failed
    }
}





