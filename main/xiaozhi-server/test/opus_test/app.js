const SAMPLE_RATE = 16000;
const CHANNELS = 1;
const FRAME_SIZE = 960;  // Corresponds to 60ms frame size (16000Hz * 0.06s = 960 samples)
const OPUS_APPLICATION = 2049; // OPUS_APPLICATION_AUDIO
const BUFFER_SIZE = 4096;

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

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
playButton.addEventListener("click", playRecording);

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

// Simulate server-returned Opus data for decoding and playback
function playOpusFromServer(opusData) {
    // This function demonstrates how to handle server-returned opus data
    // opusData should be an array containing opus frames
    
    if (!opusDecoder) {
        initOpus().then(success => {
            if (success) {
                decodeAndPlayOpusData(opusData);
            } else {
                statusLabel.textContent = "Opus decoder initialization failed";
            }
        });
    } else {
        decodeAndPlayOpusData(opusData);
    }
}

function decodeAndPlayOpusData(opusData) {
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
