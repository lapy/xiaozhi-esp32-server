// WebSocket message handling.
import { getConfig, saveConnectionUrls } from '../../config/manager.js?v=0205';
import { uiController } from '../../ui/controller.js?v=0205';
import { log } from '../../utils/logger.js?v=0205';
import { getAudioPlayer } from '../audio/player.js?v=0205';
import { getAudioRecorder } from '../audio/recorder.js?v=0205';
import { executeMcpTool, getMcpTools, setWebSocket as setMcpWebSocket } from '../mcp/tools.js?v=0205';
import { webSocketConnect } from './ota-connector.js?v=0205';

function containsBindPrompt(text = '') {
    return /(bind|binding|verification code|pair)/i.test(text) || text.includes('\u7ed1\u5b9a');
}

// WebSocket handler class.
export class WebSocketHandler {
    constructor() {
        this.websocket = null;
        this.onConnectionStateChange = null;
        this.onRecordButtonStateChange = null;
        this.onSessionStateChange = null;
        this.onSessionEmotionChange = null;
        this.onChatMessage = null; // Chat message callback.
        this.currentSessionId = null;
        this.isRemoteSpeaking = false;
    }

    // Send the initial hello handshake.
    async sendHelloMessage() {
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) return false;

        try {
            const config = getConfig();

            const helloMessage = {
                type: 'hello',
                device_id: config.deviceId,
                device_name: config.deviceName,
                device_mac: config.deviceMac,
                token: config.token,
                features: {
                    mcp: true
                }
            };

            log('Sending hello handshake.', 'info');
            this.websocket.send(JSON.stringify(helloMessage));

            return new Promise(resolve => {
                const timeout = setTimeout(() => {
                    log('Timed out while waiting for the hello response.', 'error');
                    log('Tip: use the authentication test flow to troubleshoot the connection.', 'info');
                    resolve(false);
                }, 5000);

                const onMessageHandler = (event) => {
                    try {
                        const response = JSON.parse(event.data);
                        if (response.type === 'hello' && response.session_id) {
                            log(`Server handshake succeeded. Session ID: ${response.session_id}`, 'success');
                            clearTimeout(timeout);
                            this.websocket.removeEventListener('message', onMessageHandler);
                            resolve(true);
                        }
                    } catch (e) {
                        // Ignore non-JSON messages.
                    }
                };

                this.websocket.addEventListener('message', onMessageHandler);
            });
        } catch (error) {
            log(`Failed to send the hello message: ${error.message}`, 'error');
            return false;
        }
    }

    // Handle JSON text messages.
    handleTextMessage(message) {
        if (message.type === 'hello') {
            log(`Server response: ${JSON.stringify(message, null, 2)}`, 'success');
            window.cameraAvailable = true;
            log('Connection established. The camera is now available.', 'success');
            uiController.updateDialButton(true);
            uiController.startAIChatSession();
        } else if (message.type === 'tts') {
            this.handleTTSMessage(message);
        } else if (message.type === 'audio') {
            log(`Received audio control message: ${JSON.stringify(message)}`, 'info');
        } else if (message.type === 'stt') {
            log(`Speech recognition result: ${message.text}`, 'info');
            // Check whether the device still needs to be bound.
            if (containsBindPrompt(message.text)) {
                log('Received a device binding prompt. Updating camera availability.', 'warning');
                window.cameraAvailable = false;
                // Turn the camera off.
                if (typeof window.stopCamera === 'function') {
                    window.stopCamera();
                }
                // Update the camera button state.
                const cameraBtn = document.getElementById('cameraBtn');
                if (cameraBtn) {
                    cameraBtn.classList.remove('camera-active');
                    cameraBtn.querySelector('.btn-text').textContent = 'Camera';
                    cameraBtn.disabled = true;
                    cameraBtn.title = 'Bind the device before using the camera';
                }
            }
            // Render STT text through the chat callback.
            if (this.onChatMessage && message.text) {
                this.onChatMessage(message.text, true);
            }
        } else if (message.type === 'llm') {
            log(`Model reply: ${message.text}`, 'info');
            // Render the model reply through the chat callback.
            if (this.onChatMessage && message.text) {
                this.onChatMessage(message.text, false);
            }

            // If the message includes emoji, update the session emotion state.
            if (message.text && /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u.test(message.text)) {
                // Extract the emoji.
                const emojiMatch = message.text.match(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u);
                if (emojiMatch && this.onSessionEmotionChange) {
                    this.onSessionEmotionChange(emojiMatch[0]);
                }

                // Trigger the matching Live2D emotion.
                if (message.emotion) {
                    console.log(`Received emotion payload: emotion=${message.emotion}, text=${message.text}`);
                    this.triggerLive2DEmotionAction(message.emotion);
                }
            }

            // Only render chat content when there is text beyond emoji.
            const textWithoutEmoji = message.text ? message.text.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim() : '';
            if (textWithoutEmoji && this.onChatMessage) {
                this.onChatMessage(message.text, false);
            }
        } else if (message.type === 'mcp') {
            this.handleMCPMessage(message);
        } else {
            log(`Unknown message type: ${message.type}`, 'info');
            if (this.onChatMessage) {
                this.onChatMessage(`Unknown message type: ${message.type}\n${JSON.stringify(message, null, 2)}`, false);
            }
        }
    }

    // Handle TTS state messages.
    handleTTSMessage(message) {
        if (message.state === 'start') {
            log('Server started streaming audio.', 'info');
            this.currentSessionId = message.session_id;
            this.isRemoteSpeaking = true;
            if (this.onSessionStateChange) {
                this.onSessionStateChange(true);
            }

            // Start the Live2D talking animation.
            this.startLive2DTalking();
        } else if (message.state === 'sentence_start') {
            log(`Server sent a speech segment: ${message.text}`, 'info');
            this.ttsSentenceCount = (this.ttsSentenceCount || 0) + 1;

            if (message.text && this.onChatMessage) {
                this.onChatMessage(message.text, false);
            }

            // Make sure the animation is running at sentence boundaries.
            const live2dManager = window.chatApp?.live2dManager;
            if (live2dManager && !live2dManager.isTalking) {
                this.startLive2DTalking();
            }
        } else if (message.state === 'sentence_end') {
            log(`Speech segment ended: ${message.text}`, 'info');
        } else if (message.state === 'stop') {
            log('Server audio stream ended. Clearing buffered audio.', 'info');

            // Clear all buffered audio and stop playback.
            const audioPlayer = getAudioPlayer();
            audioPlayer.clearAllAudio();

            this.isRemoteSpeaking = false;
            if (this.onRecordButtonStateChange) {
                this.onRecordButtonStateChange(false);
            }
            if (this.onSessionStateChange) {
                this.onSessionStateChange(false);
            }

            // Delay the stop so the final sentence can finish visually.
            setTimeout(() => {
                this.stopLive2DTalking();
                this.ttsSentenceCount = 0;
            }, 1000);
        }
    }

    // Start the Live2D talking animation.
    startLive2DTalking() {
        try {
            // Get the Live2D manager instance.
            const live2dManager = window.chatApp?.live2dManager;
            if (live2dManager && live2dManager.live2dModel) {
                live2dManager.startTalking();
                log('Live2D talking animation started.', 'info');
            }
        } catch (error) {
            log(`Failed to start the Live2D talking animation: ${error.message}`, 'error');
        }
    }

    // Stop the Live2D talking animation.
    stopLive2DTalking() {
        try {
            const live2dManager = window.chatApp?.live2dManager;
            if (live2dManager) {
                live2dManager.stopTalking();
                log('Live2D talking animation stopped.', 'info');
            }
        } catch (error) {
            log(`Failed to stop the Live2D talking animation: ${error.message}`, 'error');
        }
    }

    // Initialize the Live2D audio analyzer.
    initializeLive2DAudioAnalyzer() {
        try {
            const live2dManager = window.chatApp?.live2dManager;
            if (live2dManager) {
                if (live2dManager.initializeAudioAnalyzer()) {
                    log('Live2D audio analyzer initialized and connected to the player.', 'success');
                } else {
                    log('Live2D audio analyzer initialization failed. Falling back to simulated animation.', 'warning');
                }
            }
        } catch (error) {
            log(`Failed to initialize the Live2D audio analyzer: ${error.message}`, 'error');
        }
    }

    // Handle MCP messages.
    handleMCPMessage(message) {
        const payload = message.payload || {};
        log(`Server payload: ${JSON.stringify(message)}`, 'info');

        if (payload.method === 'tools/list') {
            const tools = getMcpTools();

            const replyMessage = JSON.stringify({
                "session_id": message.session_id || "",
                "type": "mcp",
                "payload": {
                    "jsonrpc": "2.0",
                    "id": payload.id,
                    "result": {
                        "tools": tools
                    }
                }
            });
            log(`Client reply: ${replyMessage}`, 'info');
            this.websocket.send(replyMessage);
            log(`Returned MCP tool list with ${tools.length} tools.`, 'info');

        } else if (payload.method === 'tools/call') {
            const toolName = payload.params?.name;
            const toolArgs = payload.params?.arguments;

            log(`Calling tool: ${toolName} args: ${JSON.stringify(toolArgs)}`, 'info');

            executeMcpTool(toolName, toolArgs).then(result => {
                const replyMessage = JSON.stringify({
                    "session_id": message.session_id || "",
                    "type": "mcp",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": payload.id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": JSON.stringify(result)
                                }
                            ],
                            "isError": false
                        }
                    }
                });

                log(`Client reply: ${replyMessage}`, 'info');
                this.websocket.send(replyMessage);
            }).catch(error => {
                log(`Tool execution failed: ${error.message}`, 'error');
                const errorReply = JSON.stringify({
                    "session_id": message.session_id || "",
                    "type": "mcp",
                    "payload": {
                        "jsonrpc": "2.0",
                        "id": payload.id,
                        "error": {
                            "code": -32603,
                            "message": error.message
                        }
                    }
                });
                this.websocket.send(errorReply);
            });
        } else if (payload.method === 'initialize') {
            log(`Received MCP initialize request: ${JSON.stringify(payload.params)}`, 'info');
            // Save the vision endpoint info.
            const visionUrl = document.getElementById('visionUrl');
            const visionConfig = payload?.params?.capabilities?.vision;
            if (visionConfig && typeof visionConfig === 'object' && visionConfig.url && visionConfig.token) {
                const visionConfigStr = JSON.stringify(visionConfig);
                localStorage.setItem('xz_tester_vision', visionConfigStr);
                if (visionUrl) visionUrl.value = visionConfig.url;
            } else {
                localStorage.removeItem('xz_tester_vision');
                if (visionUrl) visionUrl.value = '';
            }

            const replyMessage = JSON.stringify({
                "session_id": message.session_id || "",
                "type": "mcp",
                "payload": {
                    "jsonrpc": "2.0",
                    "id": payload.id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "xiaozhi-web-test",
                            "version": "2.1.0"
                        }
                    }
                }
            });
            log('Sent MCP initialize response.', 'info');
            this.websocket.send(replyMessage);
        } else {
            log(`Unknown MCP method: ${payload.method}`, 'warning');
        }
    }

    // Handle binary audio payloads.
    async handleBinaryMessage(data) {
        try {
            let arrayBuffer;
            if (data instanceof ArrayBuffer) {
                arrayBuffer = data;
            } else if (data instanceof Blob) {
                arrayBuffer = await data.arrayBuffer();
                log(`Received Blob audio payload. Size: ${arrayBuffer.byteLength} bytes.`, 'debug');
            } else {
                log(`Received an unknown binary payload type: ${typeof data}`, 'warning');
                return;
            }

            const opusData = new Uint8Array(arrayBuffer);
            const audioPlayer = getAudioPlayer();
            audioPlayer.enqueueAudioData(opusData);
        } catch (error) {
            log(`Failed to process the binary payload: ${error.message}`, 'error');
        }
    }

    // Connect to the WebSocket server.
    async connect() {
        const config = getConfig();
        log('Checking OTA endpoint status...', 'info');
        saveConnectionUrls();

        try {
            const otaUrl = document.getElementById('otaUrl').value.trim();
            const ws = await webSocketConnect(otaUrl, config);
            if (ws === undefined) {
                return false;
            }
            this.websocket = ws;

            // Receive binary data as ArrayBuffer.
            this.websocket.binaryType = 'arraybuffer';

            // Share the socket with the MCP module.
            setMcpWebSocket(this.websocket);

            // Share the socket with the audio recorder.
            const audioRecorder = getAudioRecorder();
            audioRecorder.setWebSocket(this.websocket);

            this.setupEventHandlers();

            return true;
        } catch (error) {
            log(`Connection error: ${error.message}`, 'error');
            if (this.onConnectionStateChange) {
                this.onConnectionStateChange(false);
            }
            return false;
        }
    }

    // Register WebSocket event handlers.
    setupEventHandlers() {
        this.websocket.onopen = async () => {
            const url = document.getElementById('serverUrl').value;
            log(`Connected to the server: ${url}`, 'success');

            if (this.onConnectionStateChange) {
                this.onConnectionStateChange(true);
            }

            // After connecting, default back to the listening state.
            this.isRemoteSpeaking = false;
            if (this.onSessionStateChange) {
                this.onSessionStateChange(false);
            }

            // Initialize the Live2D analyzer after the socket is ready.
            this.initializeLive2DAudioAnalyzer();

            await this.sendHelloMessage();
        };

        this.websocket.onclose = () => {
            log('Disconnected from the server.', 'info');

            if (this.onConnectionStateChange) {
                this.onConnectionStateChange(false);
            }

            const audioRecorder = getAudioRecorder();
            audioRecorder.stop();

            // Turn off the camera.
            if (typeof window.stopCamera === 'function') {
                window.stopCamera();
            }

            // Hide the camera preview.
            const cameraContainer = document.getElementById('cameraContainer');
            if (cameraContainer) {
                cameraContainer.classList.remove('active');
            }
        };

        this.websocket.onerror = (error) => {
            log(`WebSocket error: ${error.message || 'unknown error'}`, 'error');
            uiController.addChatMessage(`Warning: WebSocket error: ${error.message || 'unknown error'}`, false);
            if (this.onConnectionStateChange) {
                this.onConnectionStateChange(false);
            }
        };

        this.websocket.onmessage = (event) => {
            try {
                if (typeof event.data === 'string') {
                    const message = JSON.parse(event.data);
                    this.handleTextMessage(message);
                } else {
                    this.handleBinaryMessage(event.data);
                }
            } catch (error) {
                log(`WebSocket message handling error: ${error.message}`, 'error');
            }
        };
    }

    // Disconnect the current session.
    disconnect() {
        if (!this.websocket) return;

        this.websocket.close();
        const audioRecorder = getAudioRecorder();
        audioRecorder.stop();

        // Turn off the camera.
        if (typeof window.stopCamera === 'function') {
            window.stopCamera();
        }

        // Hide the camera preview.
        const cameraContainer = document.getElementById('cameraContainer');
        if (cameraContainer) {
            cameraContainer.classList.remove('active');
        }
    }

    // Send a text message.
    sendTextMessage(text) {
        if (text === '' || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            return false;
        }

        try {
            // If the remote side is still talking, send an abort first.
            if (this.isRemoteSpeaking && this.currentSessionId) {
                const abortMessage = {
                    session_id: this.currentSessionId,
                    type: 'abort',
                    reason: 'wake_word_detected'
                };
                this.websocket.send(JSON.stringify(abortMessage));
                log('Sent abort message.', 'info');
            }

            const listenMessage = {
                type: 'listen',
                state: 'detect',
                text: text
            };

            this.websocket.send(JSON.stringify(listenMessage));
            log(`Sent text message: ${text}`, 'info');

            return true;
        } catch (error) {
            log(`Failed to send the message: ${error.message}`, 'error');
            return false;
        }
    }

    /**
     * Trigger a Live2D emotion action.
     * @param {string} emotion - Emotion name.
     */
    triggerLive2DEmotionAction(emotion) {
        try {
            const live2dManager = window.chatApp?.live2dManager;
            if (live2dManager && typeof live2dManager.triggerEmotionAction === 'function') {
                live2dManager.triggerEmotionAction(emotion);
                log(`Triggered Live2D emotion action: ${emotion}`, 'info');
            } else {
                log('Could not trigger the Live2D emotion action because the manager or method is unavailable.', 'warning');
            }
        } catch (error) {
            log(`Failed to trigger the Live2D emotion action: ${error.message}`, 'error');
        }
    }

    // Return the raw WebSocket instance.
    getWebSocket() {
        return this.websocket;
    }

    // Check whether the socket is connected.
    isConnected() {
        return this.websocket && this.websocket.readyState === WebSocket.OPEN;
    }
}

// Create the singleton instance.
let wsHandlerInstance = null;

export function getWebSocketHandler() {
    if (!wsHandlerInstance) {
        wsHandlerInstance = new WebSocketHandler();
    }
    return wsHandlerInstance;
}
