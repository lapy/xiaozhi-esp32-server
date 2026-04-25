import { log } from '../../utils/logger.js?v=0205';

// Verify that the Opus runtime has been loaded.
export function checkOpusLoaded() {
    try {
        // Check whether the local libopus bundle exported Module.
        if (typeof Module === 'undefined') {
            throw new Error('The Opus runtime is not loaded because the Module object is missing.');
        }

        // Prefer Module.instance when libopus exports that form.
        if (typeof Module.instance !== 'undefined' && typeof Module.instance._opus_decoder_get_size === 'function') {
            // Promote Module.instance to the shared runtime handle.
            window.ModuleInstance = Module.instance;
            log('Opus runtime loaded successfully using Module.instance.', 'success');

            // Hide the status indicator after startup settles.
            const statusElement = document.getElementById('scriptStatus');
            if (statusElement) statusElement.style.display = 'none';
            return;
        }

        // Fall back to the global Module object when needed.
        if (typeof Module._opus_decoder_get_size === 'function') {
            window.ModuleInstance = Module;
            log('Opus runtime loaded successfully using the global Module object.', 'success');

            // Hide the status indicator after startup settles.
            const statusElement = document.getElementById('scriptStatus');
            if (statusElement) statusElement.style.display = 'none';
            return;
        }

        throw new Error('The expected Opus decoder exports were not found. The Module structure may be invalid.');
    } catch (err) {
        log(`Failed to load the Opus runtime. Verify that libopus.js exists and is valid: ${err.message}`, 'error');
    }
}


// Create and cache an Opus encoder.
let opusEncoder = null;
export function initOpusEncoder() {
    try {
        if (opusEncoder) {
            return opusEncoder;
        }

        if (!window.ModuleInstance) {
            log('Cannot create the Opus encoder because ModuleInstance is unavailable.', 'error');
            return;
        }

        // Initialize the encoder wrapper.
        const mod = window.ModuleInstance;
        const sampleRate = 16000; // 16 kHz sample rate
        const channels = 1;       // mono
        const application = 2048; // OPUS_APPLICATION_VOIP = 2048

        // Create the encoder wrapper.
        opusEncoder = {
            channels: channels,
            sampleRate: sampleRate,
            frameSize: 960, // 60ms @ 16kHz = 60 * 16 = 960 samples
            maxPacketSize: 4000, // maximum packet size
            module: mod,

            // Initialize the underlying encoder.
            init: function () {
                try {
                    // Get the encoder size.
                    const encoderSize = mod._opus_encoder_get_size(this.channels);
                    log(`Opus encoder size: ${encoderSize} bytes`, 'info');

                    // Allocate memory for the encoder state.
                    this.encoderPtr = mod._malloc(encoderSize);
                    if (!this.encoderPtr) {
                        throw new Error('Failed to allocate encoder memory.');
                    }

                    // Initialize the encoder.
                    const err = mod._opus_encoder_init(
                        this.encoderPtr,
                        this.sampleRate,
                        this.channels,
                        application
                    );

                    if (err < 0) {
                        throw new Error(`Opus encoder initialization failed: ${err}`);
                    }

                    // Set bitrate to 16 kbps.
                    mod._opus_encoder_ctl(this.encoderPtr, 4002, 16000); // OPUS_SET_BITRATE

                    // Set encoder complexity.
                    mod._opus_encoder_ctl(this.encoderPtr, 4010, 5);     // OPUS_SET_COMPLEXITY

                    // Enable DTX so silent frames are not transmitted.
                    mod._opus_encoder_ctl(this.encoderPtr, 4016, 1);     // OPUS_SET_DTX

                    log('Opus encoder initialized successfully.', 'success');
                    return true;
                } catch (error) {
                    if (this.encoderPtr) {
                        mod._free(this.encoderPtr);
                        this.encoderPtr = null;
                    }
                    log(`Opus encoder initialization failed: ${error.message}`, 'error');
                    return false;
                }
            },

            // Encode PCM data into Opus packets.
            encode: function (pcmData) {
                if (!this.encoderPtr) {
                    if (!this.init()) {
                        return null;
                    }
                }

                try {
                    const mod = this.module;

                    // Allocate memory for PCM input.
                    const pcmPtr = mod._malloc(pcmData.length * 2); // 2 bytes per int16

                    // Copy PCM data into the heap.
                    for (let i = 0; i < pcmData.length; i++) {
                        mod.HEAP16[(pcmPtr >> 1) + i] = pcmData[i];
                    }

                    // Allocate output memory.
                    const outPtr = mod._malloc(this.maxPacketSize);

                    // Encode the frame.
                    const encodedLen = mod._opus_encode(
                        this.encoderPtr,
                        pcmPtr,
                        this.frameSize,
                        outPtr,
                        this.maxPacketSize
                    );

                    if (encodedLen < 0) {
                        throw new Error(`Opus encoding failed: ${encodedLen}`);
                    }

                    // Copy the encoded bytes out of the heap.
                    const opusData = new Uint8Array(encodedLen);
                    for (let i = 0; i < encodedLen; i++) {
                        opusData[i] = mod.HEAPU8[outPtr + i];
                    }

                    // Release temporary allocations.
                    mod._free(pcmPtr);
                    mod._free(outPtr);

                    return opusData;
                } catch (error) {
                    log(`Opus encoding error: ${error.message}`, 'error');
                    return null;
                }
            },

            // Destroy the encoder instance.
            destroy: function () {
                if (this.encoderPtr) {
                    this.module._free(this.encoderPtr);
                    this.encoderPtr = null;
                }
            }
        };

        opusEncoder.init();
        return opusEncoder;
    } catch (error) {
        log(`Failed to create the Opus encoder: ${error.message}`, 'error');
        return false;
    }
}
