const SAMPLE_RATE = 16000;
const CHANNELS = 1;
const FRAME_SIZE = 960;  // Corresponds to 60ms frame size (16000Hz * 0.06s = 960 samples)
const OPUS_APPLICATION = 2049; // OPUS_APPLICATION_AUDIO
const BUFFER_SIZE = 4096;

// WebSocket related variables
let websocket = null;
let isConnected = false;

let audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: SAMPLE_RATE });
let mediaStream, mediaSource, audioProcessor;
let recordedPcmData = []; // Store raw PCM data
let recordedOpusData = []; // Store Opus encoded data
let opusEncoder, opusDecoder;
let isRecording = false;

const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");
const playButton = document.getElementById("play");
const statusLabel = document.getElementById("status");

// Add WebSocket interface element references
const connectButton = document.getElementById("connectButton") || document.createElement("button");
const serverUrlInput = document.getElementById("serverUrl") || document.createElement("input");
const connectionStatus = document.getElementById("connectionStatus") || document.createElement("span");
const sendTextButton = document.getElementById("sendTextButton") || document.createElement("button");
const messageInput = document.getElementById("messageInput") || document.createElement("input");
const conversationDiv = document.getElementById("conversation") || document.createElement("div");

// Add connection and send event listeners
if(connectButton.id === "connectButton") {
    connectButton.addEventListener("click", connectToServer);
}
if(sendTextButton.id === "sendTextButton") {
    sendTextButton.addEventListener("click", sendTextMessage);
}

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
playButton.addEventListener("click", playRecording);

// Audio buffering and playback management
let audioBufferQueue = [];     // Store received audio packets
let isAudioBuffering = false;  // Whether audio is being buffered
let isAudioPlaying = false;    // Whether audio is being played
const BUFFER_THRESHOLD = 3;    // Buffer packet count threshold, accumulate at least 5 packets before starting playback
const MIN_AUDIO_DURATION = 0.1; // Minimum audio length (seconds), audio shorter than this will be merged
let streamingContext = null;   // Audio stream context

// Initialize Opus encoder and decoder
async function initOpus() {
    if (typeof window.ModuleInstance === 'undefined') {
        if (typeof Module !== 'undefined') {
            // Try to use global Module
            window.ModuleInstance = Module;
            console.log('Using global Module as ModuleInstance');
        } else {
            console.error("Opus library not loaded, ModuleInstance and Module objects do not exist");
            return false;
        }
    }
    
    try {
        const mod = window.ModuleInstance;
        
        // Create encoder
        opusEncoder = {
            channels: CHANNELS,
            sampleRate: SAMPLE_RATE,
            frameSize: FRAME_SIZE,
            maxPacketSize: 4000,
            module: mod,
            
            // Initialize encoder
            init: function() {
                // Get encoder size
                const encoderSize = mod._opus_encoder_get_size(this.channels);
                console.log(`Opus encoder size: ${encoderSize} bytes`);
                
                // Allocate memory
                this.encoderPtr = mod._malloc(encoderSize);
                if (!this.encoderPtr) {
                    throw new Error("Unable to allocate encoder memory");
                }
                
                // Initialize encoder
                const err = mod._opus_encoder_init(
                    this.encoderPtr,
                    this.sampleRate,
                    this.channels,
                    OPUS_APPLICATION
                );
                
                if (err < 0) {
                    throw new Error(`Opus encoder initialization failed: ${err}`);
                }
                
                return true;
            },
            
            // Encoding method
            encode: function(pcmData) {
                const mod = this.module;
                
                // Allocate memory for PCM data
                const pcmPtr = mod._malloc(pcmData.length * 2); // Int16 = 2 bytes
                
                // Copy data to WASM memory
                for (let i = 0; i < pcmData.length; i++) {
                    mod.HEAP16[(pcmPtr >> 1) + i] = pcmData[i];
                }
                
                // Allocate memory for Opus encoded data
                const maxEncodedSize = this.maxPacketSize;
                const encodedPtr = mod._malloc(maxEncodedSize);
                
                // Encode
                const encodedBytes = mod._opus_encode(
                    this.encoderPtr,
                    pcmPtr,
                    this.frameSize,
                    encodedPtr,
                    maxEncodedSize
                );
                
                if (encodedBytes < 0) {
                    mod._free(pcmPtr);
                    mod._free(encodedPtr);
                    throw new Error(`Opus encoding failed: ${encodedBytes}`);
                }
                
                // Copy encoded data
                const encodedData = new Uint8Array(encodedBytes);
                for (let i = 0; i < encodedBytes; i++) {
                    encodedData[i] = mod.HEAPU8[encodedPtr + i];
                }
                
                // Free memory
                mod._free(pcmPtr);
                mod._free(encodedPtr);
                
                return encodedData;
            },
            
            // Destroy method
            destroy: function() {
                if (this.encoderPtr) {
                    this.module._free(this.encoderPtr);
                    this.encoderPtr = null;
                }
            }
        };
        
        // Create decoder
        opusDecoder = {
            channels: CHANNELS,
            rate: SAMPLE_RATE,
            frameSize: FRAME_SIZE,
            module: mod,
            
            // Initialize decoder
            init: function() {
                // Get decoder size
                const decoderSize = mod._opus_decoder_get_size(this.channels);
                console.log(`Opus decoder size: ${decoderSize} bytes`);
                
                // Allocate memory
                this.decoderPtr = mod._malloc(decoderSize);
                if (!this.decoderPtr) {
                    throw new Error("Unable to allocate decoder memory");
                }
                
                // Initialize decoder
                const err = mod._opus_decoder_init(
                    this.decoderPtr,
                    this.rate,
                    this.channels
                );
                
                if (err < 0) {
                    throw new Error(`Opus decoder initialization failed: ${err}`);
                }
                
                return true;
            },
            
            // Decoding method
            decode: function(opusData) {
                const mod = this.module;
                
                // Allocate memory for Opus data
                const opusPtr = mod._malloc(opusData.length);
                mod.HEAPU8.set(opusData, opusPtr);
                
                // Allocate memory for PCM output
                const pcmPtr = mod._malloc(this.frameSize * 2); // Int16 = 2 bytes
                
                // Decode
                const decodedSamples = mod._opus_decode(
                    this.decoderPtr,
                    opusPtr,
                    opusData.length,
                    pcmPtr,
                    this.frameSize,
                    0 // Do not use FEC
                );
                
                if (decodedSamples < 0) {
                    mod._free(opusPtr);
                    mod._free(pcmPtr);
                    throw new Error(`Opus decoding failed: ${decodedSamples}`);
                }
                
                // Copy decoded data
                const decodedData = new Int16Array(decodedSamples);
                for (let i = 0; i < decodedSamples; i++) {
                    decodedData[i] = mod.HEAP16[(pcmPtr >> 1) + i];
                }
                
                // Free memory
                mod._free(opusPtr);
                mod._free(pcmPtr);
                
                return decodedData;
            },
            
            // Destroy method
            destroy: function() {
                if (this.decoderPtr) {
                    this.module._free(this.decoderPtr);
                    this.decoderPtr = null;
                }
            }
        };
        
        // Initialize encoder and decoder
        if (opusEncoder.init() && opusDecoder.init()) {
            console.log("Opus encoder and decoder initialized successfully.");
            return true;
        } else {
            console.error("Opus initialization failed");
            return false;
        }
    } catch (error) {
        console.error("Opus initialization failed:", error);
        return false;
    }
}

// Convert Float32 audio data to Int16 audio data
function convertFloat32ToInt16(float32Data) {
    const int16Data = new Int16Array(float32Data.length);
    for (let i = 0; i < float32Data.length; i++) {
        // Convert [-1,1] range to [-32768,32767]
        const s = Math.max(-1, Math.min(1, float32Data[i]));
        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Data;
}

// Convert Int16 audio data to Float32 audio data
function convertInt16ToFloat32(int16Data) {
    const float32Data = new Float32Array(int16Data.length);
    for (let i = 0; i < int16Data.length; i++) {
        // Convert [-32768,32767] range to [-1,1]
        float32Data[i] = int16Data[i] / (int16Data[i] < 0 ? 0x8000 : 0x7FFF);
    }
    return float32Data;
}

function startRecording() {
    if (isRecording) return;
    
    // Ensure permissions and AudioContext is active
    if (audioContext.state === 'suspended') {
        audioContext.resume().then(() => {
            console.log("AudioContext resumed");
            continueStartRecording();
        }).catch(err => {
            console.error("Failed to resume AudioContext:", err);
            statusLabel.textContent = "Unable to activate audio context, please click again";
        });
    } else {
        continueStartRecording();
    }
}

// Actual start recording logic
function continueStartRecording() {
    // Reset recording data
    recordedPcmData = [];
    recordedOpusData = [];
    window.audioDataBuffer = new Int16Array(0); // Reset buffer
    
    // Initialize Opus
    initOpus().then(success => {
        if (!success) {
            statusLabel.textContent = "Opus initialization failed";
            return;
        }
        
        console.log("Start recording, parameters:", {
            sampleRate: SAMPLE_RATE,
            channels: CHANNELS,
            frameSize: FRAME_SIZE,
            bufferSize: BUFFER_SIZE
        });
        
        // If WebSocket is connected, send start recording signal
        if (isConnected && websocket && websocket.readyState === WebSocket.OPEN) {
            sendVoiceControlMessage('start');
        }
        
        // Request microphone permission
        navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: SAMPLE_RATE,
                channelCount: CHANNELS,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            } 
        })
        .then(stream => {
            console.log("Got microphone stream, actual parameters:", stream.getAudioTracks()[0].getSettings());
            
            // Check if stream is valid
            if (!stream || !stream.getAudioTracks().length || !stream.getAudioTracks()[0].enabled) {
                throw new Error("Invalid audio stream obtained");
            }
            
            mediaStream = stream;
            mediaSource = audioContext.createMediaStreamSource(stream);
            
            // Create ScriptProcessor (deprecated but good compatibility)
            // Try to use AudioWorklet before falling back to ScriptProcessor
            createAudioProcessor().then(processor => {
                if (processor) {
                    console.log("Using AudioWorklet for audio processing");
                    audioProcessor = processor;
                    // Connect audio processing chain
                    mediaSource.connect(audioProcessor);
                    audioProcessor.connect(audioContext.destination);
                } else {
                    console.log("Falling back to ScriptProcessor");
                    // Create ScriptProcessor node
                    audioProcessor = audioContext.createScriptProcessor(BUFFER_SIZE, CHANNELS, CHANNELS);
                    
                    // Process audio data
                    audioProcessor.onaudioprocess = processAudioData;
                    
                    // Connect audio processing chain
                    mediaSource.connect(audioProcessor);
                    audioProcessor.connect(audioContext.destination);
                }
                
                // Update UI
                isRecording = true;
                statusLabel.textContent = "Recording...";
                startButton.disabled = true;
                stopButton.disabled = false;
                playButton.disabled = true;
            }).catch(error => {
                console.error("Failed to create audio processor:", error);
                statusLabel.textContent = "Failed to create audio processor";
            });
        })
        .catch(error => {
            console.error("Failed to get microphone:", error);
            statusLabel.textContent = "Failed to get microphone: " + error.message;
        });
    });
}

// Create AudioWorklet processor
async function createAudioProcessor() {
    try {
        // Try to use more modern AudioWorklet API
        if ('AudioWorklet' in window && 'AudioWorkletNode' in window) {
            // Define AudioWorklet processor code
            const workletCode = `
                class OpusRecorderProcessor extends AudioWorkletProcessor {
                    constructor() {
                        super();
                        this.buffers = [];
                        this.frameSize = ${FRAME_SIZE};
                        this.buffer = new Float32Array(this.frameSize);
                        this.bufferIndex = 0;
                        this.isRecording = false;
                        
                        this.port.onmessage = (event) => {
                            if (event.data.command === 'start') {
                                this.isRecording = true;
                            } else if (event.data.command === 'stop') {
                                this.isRecording = false;
                                // Send final buffer
                                if (this.bufferIndex > 0) {
                                    const finalBuffer = this.buffer.slice(0, this.bufferIndex);
                                    this.port.postMessage({ buffer: finalBuffer });
                                }
                            }
                        };
                    }
                    
                    process(inputs, outputs) {
                        if (!this.isRecording) return true;
                        
                        // Get input data
                        const input = inputs[0][0]; // mono channel
                        if (!input || input.length === 0) return true;
                        
                        // Add input data to buffer
                        for (let i = 0; i < input.length; i++) {
                            this.buffer[this.bufferIndex++] = input[i];
                            
                            // When buffer is full, send to main thread
                            if (this.bufferIndex >= this.frameSize) {
                                this.port.postMessage({ buffer: this.buffer.slice() });
                                this.bufferIndex = 0;
                            }
                        }
                        
                        return true;
                    }
                }
                
                registerProcessor('opus-recorder-processor', OpusRecorderProcessor);
            `;
            
            // Create Blob URL
            const blob = new Blob([workletCode], { type: 'application/javascript' });
            const url = URL.createObjectURL(blob);
            
            // Load AudioWorklet module
            await audioContext.audioWorklet.addModule(url);
            
            // Create AudioWorkletNode
            const workletNode = new AudioWorkletNode(audioContext, 'opus-recorder-processor');
            
            // Handle messages received from AudioWorklet
            workletNode.port.onmessage = (event) => {
                if (event.data.buffer) {
                    // Use same processing logic as ScriptProcessor
                    processAudioData({
                        inputBuffer: {
                            getChannelData: () => event.data.buffer
                        }
                    });
                }
            };
            
            // Start recording
            workletNode.port.postMessage({ command: 'start' });
            
            // Save stop function
            workletNode.stopRecording = () => {
                workletNode.port.postMessage({ command: 'stop' });
            };
            
            console.log("AudioWorklet audio processor created successfully");
            return workletNode;
        }
    } catch (error) {
        console.error("Failed to create AudioWorklet, will use ScriptProcessor:", error);
    }
    
    // If AudioWorklet is unavailable or fails, return null to fall back to ScriptProcessor
    return null;
}

// Process audio data
function processAudioData(e) {
    // Get input buffer
    const inputBuffer = e.inputBuffer;
    
    // Get Float32 data from first channel
    const inputData = inputBuffer.getChannelData(0);
    
    // Add debug information
    const nonZeroCount = Array.from(inputData).filter(x => Math.abs(x) > 0.001).length;
    console.log(`Received audio data: ${inputData.length} samples, non-zero samples: ${nonZeroCount}`);
    
    // If all are 0, microphone may not be capturing sound correctly
    if (nonZeroCount < 5) {
        console.warn("Warning: Detected many silent samples, please check if microphone is working properly");
        // Continue processing in case some samples are indeed silent
    }
    
    // Store PCM data for debugging
    recordedPcmData.push(new Float32Array(inputData));
    
    // Convert to Int16 data for Opus encoding
    const int16Data = convertFloat32ToInt16(inputData);
    
    // If collected data is not a multiple of FRAME_SIZE, processing is needed
    // Create static buffer to store data insufficient for one frame
    if (!window.audioDataBuffer) {
        window.audioDataBuffer = new Int16Array(0);
    }
    
    // Merge previously cached data and new data
    const combinedData = new Int16Array(window.audioDataBuffer.length + int16Data.length);
    combinedData.set(window.audioDataBuffer);
    combinedData.set(int16Data, window.audioDataBuffer.length);
    
    // Process complete frames
    const frameCount = Math.floor(combinedData.length / FRAME_SIZE);
    console.log(`Encodable complete frames: ${frameCount}, total buffer size: ${combinedData.length}`);
    
    for (let i = 0; i < frameCount; i++) {
        const frameData = combinedData.subarray(i * FRAME_SIZE, (i + 1) * FRAME_SIZE);
        
        try {
            console.log(`Encoding frame ${i+1}/${frameCount}, frame size: ${frameData.length}`);
            const encodedData = opusEncoder.encode(frameData);
            if (encodedData) {
                console.log(`Encoding successful: ${encodedData.length} bytes`);
                recordedOpusData.push(encodedData);
                
                // If WebSocket is connected, send encoded data
                if (isConnected && websocket && websocket.readyState === WebSocket.OPEN) {
                    sendOpusDataToServer(encodedData);
                }
            }
        } catch (error) {
            console.error(`Opus encoding frame ${i+1} failed:`, error);
        }
    }
    
    // Save remaining data insufficient for one frame
    const remainingSamples = combinedData.length % FRAME_SIZE;
    if (remainingSamples > 0) {
        window.audioDataBuffer = combinedData.subarray(frameCount * FRAME_SIZE);
        console.log(`Keeping ${remainingSamples} samples for next processing`);
    } else {
        window.audioDataBuffer = new Int16Array(0);
    }
}

function stopRecording() {
    if (!isRecording) return;
    
    // Process remaining buffered data
    if (window.audioDataBuffer && window.audioDataBuffer.length > 0) {
        console.log(`Stop recording, processing remaining ${window.audioDataBuffer.length} samples`);
        // If remaining data is insufficient for one frame, pad with zeros to make one frame
        if (window.audioDataBuffer.length < FRAME_SIZE) {
            const paddedFrame = new Int16Array(FRAME_SIZE);
            paddedFrame.set(window.audioDataBuffer);
            // Fill remaining part with zeros
            for (let i = window.audioDataBuffer.length; i < FRAME_SIZE; i++) {
                paddedFrame[i] = 0;
            }
            try {
                console.log(`Encoding last frame (zero-padded): ${paddedFrame.length} samples`);
                const encodedData = opusEncoder.encode(paddedFrame);
                if (encodedData) {
                    recordedOpusData.push(encodedData);
                    
                    // If WebSocket is connected, send last frame
                    if (isConnected && websocket && websocket.readyState === WebSocket.OPEN) {
                        sendOpusDataToServer(encodedData);
                    }
                }
            } catch (error) {
                console.error("Last frame Opus encoding failed:", error);
            }
        } else {
            // If data exceeds one frame, process normally
            processAudioData({
                inputBuffer: {
                    getChannelData: () => convertInt16ToFloat32(window.audioDataBuffer)
                }
            });
        }
        window.audioDataBuffer = null;
    }
    
    // If WebSocket is connected, send stop recording signal
    if (isConnected && websocket && websocket.readyState === WebSocket.OPEN) {
        // Send an empty frame as end marker
        const emptyFrame = new Uint8Array(0);
        websocket.send(emptyFrame);
        
        // Send stop recording control message
        sendVoiceControlMessage('stop');
    }
    
    // If using AudioWorklet, call its specific stop method
    if (audioProcessor && typeof audioProcessor.stopRecording === 'function') {
        audioProcessor.stopRecording();
    }
    
    // Stop microphone
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    
    // Disconnect audio processing chain
    if (audioProcessor) {
        try {
            audioProcessor.disconnect();
            if (mediaSource) mediaSource.disconnect();
        } catch (error) {
            console.warn("Error disconnecting audio processing chain:", error);
        }
    }
    
    // Update UI
    isRecording = false;
    statusLabel.textContent = "Recording stopped, collected " + recordedOpusData.length + " Opus data frames";
    startButton.disabled = false;
    stopButton.disabled = true;
    playButton.disabled = recordedOpusData.length === 0;
    
    console.log("Recording completed:", 
                "PCM frames:", recordedPcmData.length, 
                "Opus frames:", recordedOpusData.length);
}

function playRecording() {
    if (!recordedOpusData.length) {
        statusLabel.textContent = "No recording to play";
        return;
    }
    
    // Decode all Opus data to PCM
    let allDecodedData = [];
    
    for (const opusData of recordedOpusData) {
        try {
            // Decode to Int16 data
            const decodedData = opusDecoder.decode(opusData);
            
            if (decodedData && decodedData.length > 0) {
                // Convert Int16 data to Float32
                const float32Data = convertInt16ToFloat32(decodedData);
                
                // Add to total decoded data
                allDecodedData.push(...float32Data);
            }
        } catch (error) {
            console.error("Opus decoding failed:", error);
        }
    }
    
    // If no data was decoded, return
    if (allDecodedData.length === 0) {
        statusLabel.textContent = "Decoding failed, cannot play";
        return;
    }
    
    // Create audio buffer
    const audioBuffer = audioContext.createBuffer(CHANNELS, allDecodedData.length, SAMPLE_RATE);
    audioBuffer.copyToChannel(new Float32Array(allDecodedData), 0);
    
    // Create audio source and play
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
    
    // Update UI
    statusLabel.textContent = "Playing...";
    playButton.disabled = true;
    
    // Restore UI after playback ends
    source.onended = () => {
        statusLabel.textContent = "Playback completed";
        playButton.disabled = false;
    };
}

// Modified version for handling binary messages
async function handleBinaryMessage(data) {
    try {
        let arrayBuffer;

        // Process based on data type
        if (data instanceof ArrayBuffer) {
            arrayBuffer = data;
            console.log(`Received ArrayBuffer audio data, size: ${data.byteLength} bytes`);
        } else if (data instanceof Blob) {
            // If it's Blob type, convert to ArrayBuffer
            arrayBuffer = await data.arrayBuffer();
            console.log(`Received Blob audio data, size: ${arrayBuffer.byteLength} bytes`);
        } else {
            console.warn(`Received unknown type of binary data: ${typeof data}`);
            return;
        }

        // Create Uint8Array for processing
        const opusData = new Uint8Array(arrayBuffer);

        if (opusData.length > 0) {
            // Add data to buffer queue
            audioBufferQueue.push(opusData);
            
            // If this is the first audio packet received, start buffering process
            if (audioBufferQueue.length === 1 && !isAudioBuffering && !isAudioPlaying) {
                startAudioBuffering();
            }
        } else {
            console.warn('Received empty audio data frame, possibly end marker');
            
            // If there's data in buffer queue and not playing, start playing immediately
            if (audioBufferQueue.length > 0 && !isAudioPlaying) {
                playBufferedAudio();
            }
            
            // If currently playing, send end signal
            if (isAudioPlaying && streamingContext) {
                streamingContext.endOfStream = true;
            }
        }
    } catch (error) {
        console.error(`Error processing binary message:`, error);
    }
}

// Start audio buffering process
function startAudioBuffering() {
    if (isAudioBuffering || isAudioPlaying) return;
    
    isAudioBuffering = true;
    console.log("Starting audio buffering...");
    
    // Set timeout, if not enough audio packets collected within certain time, start playing
    setTimeout(() => {
        if (isAudioBuffering && audioBufferQueue.length > 0) {
            console.log(`Buffer timeout, current buffered packets: ${audioBufferQueue.length}, starting playback`);
            playBufferedAudio();
        }
    }, 300); // 300ms timeout
    
    // Monitor buffering progress
    const bufferCheckInterval = setInterval(() => {
        if (!isAudioBuffering) {
            clearInterval(bufferCheckInterval);
            return;
        }
        
        // When enough audio packets accumulated, start playing
        if (audioBufferQueue.length >= BUFFER_THRESHOLD) {
            clearInterval(bufferCheckInterval);
            console.log(`Buffered ${audioBufferQueue.length} audio packets, starting playback`);
            playBufferedAudio();
        }
    }, 50);
}

// Play buffered audio
function playBufferedAudio() {
    if (isAudioPlaying || audioBufferQueue.length === 0) return;
    
    isAudioPlaying = true;
    isAudioBuffering = false;
    
    // Create streaming playback context
    if (!streamingContext) {
        streamingContext = {
            queue: [],          // Decoded PCM queue
            playing: false,     // Whether currently playing
            endOfStream: false, // Whether end signal received
            source: null,       // Current audio source
            totalSamples: 0,    // Total accumulated samples
            lastPlayTime: 0,    // Last playback timestamp
            // Decode Opus data to PCM
            decodeOpusFrames: async function(opusFrames) {
                let decodedSamples = [];
                
                for (const frame of opusFrames) {
                    try {
                        // Use Opus decoder to decode
                        const frameData = opusDecoder.decode(frame);
                        if (frameData && frameData.length > 0) {
                            // Convert to Float32
                            const floatData = convertInt16ToFloat32(frameData);
                            decodedSamples.push(...floatData);
                        }
                    } catch (error) {
                        console.error("Opus decoding failed:", error);
                    }
                }
                
                if (decodedSamples.length > 0) {
                    // Add to decoded queue
                    this.queue.push(...decodedSamples);
                    this.totalSamples += decodedSamples.length;
                    
                    // If accumulated at least 0.2 seconds of audio, start playing
                    const minSamples = SAMPLE_RATE * MIN_AUDIO_DURATION;
                    if (!this.playing && this.queue.length >= minSamples) {
                        this.startPlaying();
                    }
                }
            },
            // Start playing audio
            startPlaying: function() {
                if (this.playing || this.queue.length === 0) return;
                
                this.playing = true;
                
                // Create new audio buffer
                const minPlaySamples = Math.min(this.queue.length, SAMPLE_RATE); // Play at most 1 second
                const currentSamples = this.queue.splice(0, minPlaySamples);
                
                const audioBuffer = audioContext.createBuffer(CHANNELS, currentSamples.length, SAMPLE_RATE);
                audioBuffer.copyToChannel(new Float32Array(currentSamples), 0);
                
                // Create audio source
                this.source = audioContext.createBufferSource();
                this.source.buffer = audioBuffer;
                
                // Create gain node for smooth transition
                const gainNode = audioContext.createGain();
                
                // Apply fade in/out effect to avoid popping
                const fadeDuration = 0.02; // 20 milliseconds
                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(1, audioContext.currentTime + fadeDuration);
                
                const duration = audioBuffer.duration;
                if (duration > fadeDuration * 2) {
                    gainNode.gain.setValueAtTime(1, audioContext.currentTime + duration - fadeDuration);
                    gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + duration);
                }
                
                // Connect nodes and start playing
                this.source.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                this.lastPlayTime = audioContext.currentTime;
                console.log(`Starting playback of ${currentSamples.length} samples, about ${(currentSamples.length / SAMPLE_RATE).toFixed(2)} seconds`);
                
                // Handle after playback ends
                this.source.onended = () => {
                    this.source = null;
                    this.playing = false;
                    
                    // If queue has more data or buffer has new data, continue playing
                    if (this.queue.length > 0) {
                        setTimeout(() => this.startPlaying(), 10);
                    } else if (audioBufferQueue.length > 0) {
                        // Buffer has new data, decode it
                        const frames = [...audioBufferQueue];
                        audioBufferQueue = [];
                        this.decodeOpusFrames(frames);
                    } else if (this.endOfStream) {
                        // Stream ended and no more data
                        console.log("Audio playback completed");
                        isAudioPlaying = false;
                        streamingContext = null;
                    } else {
                        // Wait for more data
                        setTimeout(() => {
                            // If still no new data, but more packets arrived
                            if (this.queue.length === 0 && audioBufferQueue.length > 0) {
                                const frames = [...audioBufferQueue];
                                audioBufferQueue = [];
                                this.decodeOpusFrames(frames);
                            } else if (this.queue.length === 0 && audioBufferQueue.length === 0) {
                                // Really no more data
                                console.log("Audio playback completed (timeout)");
                                isAudioPlaying = false;
                                streamingContext = null;
                            }
                        }, 500); // 500ms timeout
                    }
                };
                
                this.source.start();
            }
        };
    }
    
    // Start processing buffered data
    const frames = [...audioBufferQueue];
    audioBufferQueue = []; // Clear buffer queue
    
    // Decode and play
    streamingContext.decodeOpusFrames(frames);
}

// Keep old playOpusFromServer function as backup method
function playOpusFromServerOld(opusData) {
    if (!opusDecoder) {
        initOpus().then(success => {
            if (success) {
                decodeAndPlayOpusDataOld(opusData);
            } else {
                statusLabel.textContent = "Opus decoder initialization failed";
            }
        });
    } else {
        decodeAndPlayOpusDataOld(opusData);
    }
}

// Old decode and play function as backup
function decodeAndPlayOpusDataOld(opusData) {
    let allDecodedData = [];
    
    for (const frame of opusData) {
        try {
            const decodedData = opusDecoder.decode(frame);
            if (decodedData && decodedData.length > 0) {
                const float32Data = convertInt16ToFloat32(decodedData);
                allDecodedData.push(...float32Data);
            }
        } catch (error) {
            console.error("Server Opus data decoding failed:", error);
        }
    }
    
    if (allDecodedData.length === 0) {
        statusLabel.textContent = "Server data decoding failed";
        return;
    }
    
    const audioBuffer = audioContext.createBuffer(CHANNELS, allDecodedData.length, SAMPLE_RATE);
    audioBuffer.copyToChannel(new Float32Array(allDecodedData), 0);
    
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
    
    statusLabel.textContent = "Playing server data...";
    source.onended = () => statusLabel.textContent = "Server data playback completed";
}

// Update playOpusFromServer function to Promise version
function playOpusFromServer(opusData) {
    // For compatibility, add opusData to audioBufferQueue and trigger playback
    if (Array.isArray(opusData) && opusData.length > 0) {
        for (const frame of opusData) {
            audioBufferQueue.push(frame);
        }
        
        // If not playing and buffering, start the process
        if (!isAudioBuffering && !isAudioPlaying) {
            startAudioBuffering();
        }
        
        return new Promise(resolve => {
            // We can't accurately know when playback is complete, so set a reasonable timeout
            setTimeout(resolve, 1000); // Consider processed after 1 second
        });
    } else {
        // If not array or empty, use old method
        return new Promise(resolve => {
            playOpusFromServerOld(opusData);
            setTimeout(resolve, 1000);
        });
    }
}

// Connect to WebSocket server
function connectToServer() {
    let url = serverUrlInput.value || "ws://127.0.0.1:8000/xiaozhi/v1/";
    
    try {
        // Check URL format
        if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
            console.error('URL format error, must start with ws:// or wss://');
            updateStatus('URL format error, must start with ws:// or wss://', 'error');
            return;
        }

        // Add authentication parameters
        let connUrl = new URL(url);
        connUrl.searchParams.append('device_id', 'web_test_device');
        connUrl.searchParams.append('device_mac', '00:11:22:33:44:55');

        console.log(`Connecting: ${connUrl.toString()}`);
        updateStatus(`Connecting: ${connUrl.toString()}`, 'info');
        
        websocket = new WebSocket(connUrl.toString());

        // Set binary data reception type to ArrayBuffer
        websocket.binaryType = 'arraybuffer';

        websocket.onopen = async () => {
            console.log(`Connected to server: ${url}`);
            updateStatus(`Connected to server: ${url}`, 'success');
            isConnected = true;

            // Send hello message after successful connection
            await sendHelloMessage();

            if(connectButton.id === "connectButton") {
                connectButton.textContent = 'Disconnect';
                // connectButton.onclick = disconnectFromServer;
                connectButton.removeEventListener("click", connectToServer);
                connectButton.addEventListener("click", disconnectFromServer);
            }
            
            if(messageInput.id === "messageInput") {
                messageInput.disabled = false;
            }
            
            if(sendTextButton.id === "sendTextButton") {
                sendTextButton.disabled = false;
            }
        };

        websocket.onclose = () => {
            console.log('Disconnected');
            updateStatus('Disconnected', 'info');
            isConnected = false;

            if(connectButton.id === "connectButton") {
                connectButton.textContent = 'Connect';
                // connectButton.onclick = connectToServer;
                connectButton.removeEventListener("click", disconnectFromServer);
                connectButton.addEventListener("click", connectToServer);
            }
            
            if(messageInput.id === "messageInput") {
                messageInput.disabled = true;
            }
            
            if(sendTextButton.id === "sendTextButton") {
                sendTextButton.disabled = true;
            }
        };

        websocket.onerror = (error) => {
            console.error(`WebSocket error:`, error);
            updateStatus(`WebSocket error`, 'error');
        };

        websocket.onmessage = function (event) {
            try {
                // Check if it's a text message
                if (typeof event.data === 'string') {
                    const message = JSON.parse(event.data);
                    handleTextMessage(message);
                } else {
                    // Handle binary data
                    handleBinaryMessage(event.data);
                }
            } catch (error) {
                console.error(`WebSocket message processing error:`, error);
                // Non-JSON format text messages display directly
                if (typeof event.data === 'string') {
                    addMessage(event.data);
                }
            }
        };

        updateStatus('Connecting...', 'info');
    } catch (error) {
        console.error(`Connection error:`, error);
        updateStatus(`Connection failed: ${error.message}`, 'error');
    }
}

// Disconnect WebSocket connection
function disconnectFromServer() {
    if (!websocket) return;

    websocket.close();
    if (isRecording) {
        stopRecording();
    }
}

// Send hello handshake message
async function sendHelloMessage() {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return;

    try {
        // Set device information
        const helloMessage = {
            type: 'hello',
            device_id: 'web_test_device',
            device_name: 'Web Test Device',
            device_mac: '00:11:22:33:44:55',
            token: 'your-token1' // Use token configured in config.yaml
        };

        console.log('Sending hello handshake message');
        websocket.send(JSON.stringify(helloMessage));

        // Wait for server response
        return new Promise(resolve => {
            // 5 second timeout
            const timeout = setTimeout(() => {
                console.error('Hello response timeout');
                resolve(false);
            }, 5000);

            // Temporarily listen for one message to receive hello response
            const onMessageHandler = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    if (response.type === 'hello' && response.session_id) {
                        console.log(`Server handshake successful, session ID: ${response.session_id}`);
                        clearTimeout(timeout);
                        websocket.removeEventListener('message', onMessageHandler);
                        resolve(true);
                    }
                } catch (e) {
                    // Ignore non-JSON messages
                }
            };

            websocket.addEventListener('message', onMessageHandler);
        });
    } catch (error) {
        console.error(`Send hello message error:`, error);
        return false;
    }
}

// Send text message
function sendTextMessage() {
    const message = messageInput ? messageInput.value.trim() : "";
    if (message === '' || !websocket || websocket.readyState !== WebSocket.OPEN) return;

    try {
        // Send listen message
        const listenMessage = {
            type: 'listen',
            mode: 'manual',
            state: 'detect',
            text: message
        };

        websocket.send(JSON.stringify(listenMessage));
        addMessage(message, true);
        console.log(`Sending text message: ${message}`);

        if (messageInput) {
            messageInput.value = '';
        }
    } catch (error) {
        console.error(`Send message error:`, error);
    }
}

// Add message to conversation record
function addMessage(text, isUser = false) {
    if (!conversationDiv) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'server'}`;
    messageDiv.textContent = text;
    conversationDiv.appendChild(messageDiv);
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

// Update status information
function updateStatus(message, type = 'info') {
    console.log(`[${type}] ${message}`);
    if (statusLabel) {
        statusLabel.textContent = message;
    }
    if (connectionStatus) {
        connectionStatus.textContent = message;
        switch(type) {
            case 'success':
                connectionStatus.style.color = 'green';
                break;
            case 'error':
                connectionStatus.style.color = 'red';
                break;
            case 'info':
            default:
                connectionStatus.style.color = 'black';
                break;
        }
    }
}

// Handle text message
function handleTextMessage(message) {
    if (message.type === 'hello') {
        console.log(`Server response: ${JSON.stringify(message, null, 2)}`);
    } else if (message.type === 'tts') {
        // TTS status message
        if (message.state === 'start') {
            console.log('Server started sending speech');
        } else if (message.state === 'sentence_start') {
            console.log(`Server sending speech segment: ${message.text}`);
            // Add text to conversation record
            if (message.text) {
                addMessage(message.text);
            }
        } else if (message.state === 'sentence_end') {
            console.log(`Speech segment ended: ${message.text}`);
        } else if (message.state === 'stop') {
            console.log('Server speech transmission ended');
        }
    } else if (message.type === 'audio') {
        // Audio control message
        console.log(`Received audio control message: ${JSON.stringify(message)}`);
    } else if (message.type === 'stt') {
        // Speech recognition result
        console.log(`Recognition result: ${message.text}`);
        // Add recognition result to conversation record
        addMessage(`[Speech Recognition] ${message.text}`, true);
    } else if (message.type === 'llm') {
        // Large model response
        console.log(`Large model response: ${message.text}`);
        // Add large model response to conversation record
        if (message.text && message.text !== '😊') {
            addMessage(message.text);
        }
    } else {
        // Unknown message type
        console.log(`Unknown message type: ${message.type}`);
        addMessage(JSON.stringify(message, null, 2));
    }
}

// Send audio data to WebSocket
function sendOpusDataToServer(opusData) {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected, cannot send audio data');
        return false;
    }

    try {
        // Send binary data
        websocket.send(opusData.buffer);
        console.log(`Sent Opus audio data: ${opusData.length} bytes`);
        return true;
    } catch (error) {
        console.error(`Failed to send audio data:`, error);
        return false;
    }
}

// Send voice start and end signals
function sendVoiceControlMessage(state) {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return;

    try {
        const message = {
            type: 'listen',
            mode: 'manual',
            state: state  // 'start' or 'stop'
        };

        websocket.send(JSON.stringify(message));
        console.log(`Send voice ${state === 'start' ? 'start' : 'end'} control message`);
    } catch (error) {
        console.error(`Failed to send voice control message:`, error);
    }
}
