import BlockingQueue from '../../utils/blocking-queue.js?v=0205';
import { log } from '../../utils/logger.js?v=0205';

// Streaming audio playback context.
export class StreamingContext {
    constructor(opusDecoder, audioContext, sampleRate, channels, minAudioDuration) {
        this.opusDecoder = opusDecoder;
        this.audioContext = audioContext;

        // Audio parameters.
        this.sampleRate = sampleRate;
        this.channels = channels;
        this.minAudioDuration = minAudioDuration;

        // Queues and playback state.
        this.queue = [];          // decoded PCM samples currently queued for playback
        this.activeQueue = new BlockingQueue(); // decoded PCM samples ready to play
        this.pendingAudioBufferQueue = [];  // compressed frames waiting to be decoded
        this.audioBufferQueue = new BlockingQueue();  // compressed frame queue
        this.playing = false;     // whether playback is active
        this.endOfStream = false; // whether an end-of-stream marker was received
        this.source = null;       // current audio source
        this.totalSamples = 0;    // cumulative decoded samples
        this.lastPlayTime = 0;    // timestamp of the most recent scheduled playback
        this.scheduledEndTime = 0; // end time of already scheduled audio

        // Analyzer node used by Live2D.
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
    }

    // Queue compressed audio frames.
    pushAudioBuffer(item) {
        this.audioBufferQueue.enqueue(...item);
    }

    // Wait for compressed frames and move them into the pending decode queue.
    async getPendingAudioBufferQueue() {
        const data = await this.audioBufferQueue.dequeue();
        this.pendingAudioBufferQueue = data;
    }

    // Wait for enough decoded samples to continue playback.
    async getQueue(minSamples) {
        const num = minSamples - this.queue.length > 0 ? minSamples - this.queue.length : 1;
        const tempArray = await this.activeQueue.dequeue(num);
        this.queue.push(...tempArray);
    }

    // Convert Int16 audio into Float32 audio.
    convertInt16ToFloat32(int16Data) {
        const float32Data = new Float32Array(int16Data.length);
        for (let i = 0; i < int16Data.length; i++) {
            // Convert [-32768, 32767] into [-1, 1] using 32768.0 to avoid asymmetric clipping.
            float32Data[i] = int16Data[i] / 32768.0;
        }
        return float32Data;
    }

    // Return the number of compressed frames waiting to be decoded.
    getPendingDecodeCount() {
        return this.audioBufferQueue.length + this.pendingAudioBufferQueue.length;
    }

    // Return the number of queued playback packets (assuming 960 samples per packet).
    getPendingPlayCount() {
        // Samples already in the decoded queues.
        const queuedSamples = this.activeQueue.length + this.queue.length;

        // Samples already scheduled but not yet played.
        let scheduledSamples = 0;
        if (this.playing && this.scheduledEndTime) {
            const currentTime = this.audioContext.currentTime;
            const remainingTime = Math.max(0, this.scheduledEndTime - currentTime);
            scheduledSamples = Math.floor(remainingTime * this.sampleRate);
        }

        const totalSamples = queuedSamples + scheduledSamples;
        return Math.ceil(totalSamples / 960);
    }

    // Clear all playback buffers and reset state.
    clearAllBuffers() {
        log('Clearing all audio buffers.', 'info');

        // Clear all queues while preserving object references.
        this.audioBufferQueue.clear();
        this.pendingAudioBufferQueue = [];
        this.activeQueue.clear();
        this.queue = [];

        // Stop the current audio source.
        if (this.source) {
            try {
                this.source.stop();
                this.source.disconnect();
            } catch (e) {
                // Ignore already-stopped source errors.
            }
            this.source = null;
        }

        // Reset playback state.
        this.playing = false;
        this.scheduledEndTime = this.audioContext.currentTime;
        this.totalSamples = 0;

        log('Audio buffers cleared.', 'success');
    }

    // Return the analyzer node for Live2D.
    getAnalyser() {
        return this.analyser;
    }

    // Decode queued Opus frames into PCM.
    async decodeOpusFrames() {
        if (!this.opusDecoder) {
            log('The Opus decoder is not initialized, so decoding cannot start.', 'error');
            return;
        } else {
            log('Opus decoder started.', 'info');
        }

        while (true) {
            let decodedSamples = [];
            for (const frame of this.pendingAudioBufferQueue) {
                try {
                    // Decode each Opus frame.
                    const frameData = this.opusDecoder.decode(frame);
                    if (frameData && frameData.length > 0) {
                        // Convert to Float32 for Web Audio playback.
                        const floatData = this.convertInt16ToFloat32(frameData);
                        // Avoid spread syntax for large arrays.
                        for (let i = 0; i < floatData.length; i++) {
                            decodedSamples.push(floatData[i]);
                        }
                    }
                } catch (error) {
                    log('Opus decoding failed: ' + error.message, 'error');
                }
            }

            if (decodedSamples.length > 0) {
                // Avoid spread syntax for large arrays.
                for (let i = 0; i < decodedSamples.length; i++) {
                    this.activeQueue.enqueue(decodedSamples[i]);
                }
                this.totalSamples += decodedSamples.length;
            } else {
                log('No samples were decoded successfully.', 'warning');
            }
            await this.getPendingAudioBufferQueue();
        }
    }

    // Start scheduled playback.
    async startPlaying() {
        this.scheduledEndTime = this.audioContext.currentTime;

        while (true) {
            // Wait for an initial buffer before starting playback.
            const minSamples = this.sampleRate * this.minAudioDuration * 2;
            if (!this.playing && this.queue.length < minSamples) {
                await this.getQueue(minSamples);
            }
            this.playing = true;

            // Keep scheduling small playback chunks.
            while (this.playing && this.queue.length > 0) {
                // Play roughly 120 ms of audio per chunk.
                const playDuration = 0.12;
                const targetSamples = Math.floor(this.sampleRate * playDuration);
                const actualSamples = Math.min(this.queue.length, targetSamples);

                if (actualSamples === 0) break;

                const currentSamples = this.queue.splice(0, actualSamples);
                const audioBuffer = this.audioContext.createBuffer(this.channels, currentSamples.length, this.sampleRate);
                audioBuffer.copyToChannel(new Float32Array(currentSamples), 0);

                // Create the audio source.
                this.source = this.audioContext.createBufferSource();
                this.source.buffer = audioBuffer;

                // Schedule playback precisely.
                const currentTime = this.audioContext.currentTime;
                const startTime = Math.max(this.scheduledEndTime, currentTime);

                // Connect to the analyzer and output.
                this.source.connect(this.analyser);
                this.source.connect(this.audioContext.destination);

                log(`Scheduled playback for ${currentSamples.length} samples, about ${(currentSamples.length / this.sampleRate).toFixed(2)} seconds.`, 'debug');
                this.source.start(startTime);

                // Track when the next chunk can be scheduled.
                const duration = audioBuffer.duration;
                this.scheduledEndTime = startTime + duration;
                this.lastPlayTime = startTime;

                // If the queue is running low, wait for more data.
                if (this.queue.length < targetSamples) {
                    break;
                }
            }

            // Wait for more decoded samples.
            await this.getQueue(minSamples);
        }
    }
}

// Create a streaming context instance.
export function createStreamingContext(opusDecoder, audioContext, sampleRate, channels, minAudioDuration) {
    return new StreamingContext(opusDecoder, audioContext, sampleRate, channels, minAudioDuration);
}
