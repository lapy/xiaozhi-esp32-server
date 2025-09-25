import BlockingQueue from './utils/BlockingQueue.js';
import { log } from './utils/logger.js';

// Audio stream playback context class
export class StreamingContext {
    constructor(opusDecoder, audioContext, sampleRate, channels, minAudioDuration) {
        this.opusDecoder = opusDecoder;
        this.audioContext = audioContext;

        // Audio parameters
        this.sampleRate = sampleRate;
        this.channels = channels;
        this.minAudioDuration = minAudioDuration;

        // Initialize queues and state
        this.queue = [];          // Decoded PCM queue. Currently playing
        this.activeQueue = new BlockingQueue(); // Decoded PCM queue. Ready to play
        this.pendingAudioBufferQueue = [];  // Pending cache queue
        this.audioBufferQueue = new BlockingQueue();  // Cache queue
        this.playing = false;     // Whether currently playing
        this.endOfStream = false; // Whether end signal received
        this.source = null;       // Current audio source
        this.totalSamples = 0;    // Total accumulated samples
        this.lastPlayTime = 0;    // Last playback timestamp
    }

    // Cache audio array
    pushAudioBuffer(item) {
        this.audioBufferQueue.enqueue(...item);
    }

    // Get pending cache queue, single thread: no security issues when audioBufferQueue is continuously updated
    async getPendingAudioBufferQueue() {
        // Atomic exchange + clear
        [this.pendingAudioBufferQueue, this.audioBufferQueue] = [await this.audioBufferQueue.dequeue(), new BlockingQueue()];
    }

    // Get currently playing decoded PCM queue, single thread: no security issues when activeQueue is continuously updated
    async getQueue(minSamples) {
        let TepArray = [];
        const num = minSamples - this.queue.length > 0 ? minSamples - this.queue.length : 1;
        // Atomic exchange + clear
        [TepArray, this.activeQueue] = [await this.activeQueue.dequeue(num), new BlockingQueue()];
        this.queue.push(...TepArray);
    }

    // Convert Int16 audio data to Float32 audio data
    convertInt16ToFloat32(int16Data) {
        const float32Data = new Float32Array(int16Data.length);
        for (let i = 0; i < int16Data.length; i++) {
            // Convert [-32768,32767] range to [-1,1]
            float32Data[i] = int16Data[i] / (int16Data[i] < 0 ? 0x8000 : 0x7FFF);
        }
        return float32Data;
    }

    // Decode Opus data to PCM
    async decodeOpusFrames() {
        if (!this.opusDecoder) {
            log('Opus decoder not initialized, cannot decode', 'error');
            return;
        } else {
            log('Opus decoder started', 'info');
        }

        while (true) {
            let decodedSamples = [];
            for (const frame of this.pendingAudioBufferQueue) {
                try {
                    // Use Opus decoder to decode
                    const frameData = this.opusDecoder.decode(frame);
                    if (frameData && frameData.length > 0) {
                        // Convert to Float32
                        const floatData = this.convertInt16ToFloat32(frameData);
                        // Use loop instead of spread operator
                        for (let i = 0; i < floatData.length; i++) {
                            decodedSamples.push(floatData[i]);
                        }
                    }
                } catch (error) {
                    log("Opus decoding failed: " + error.message, 'error');
                }
            }

            if (decodedSamples.length > 0) {
                // Use loop instead of spread operator
                for (let i = 0; i < decodedSamples.length; i++) {
                    this.activeQueue.enqueue(decodedSamples[i]);
                }
                this.totalSamples += decodedSamples.length;
            } else {
                log('No successfully decoded samples', 'warning');
            }
            await this.getPendingAudioBufferQueue();
        }
    }

    // Start playing audio
    async startPlaying() {
        while (true) {
            // If accumulated at least 0.3 seconds of audio, start playing
            const minSamples = this.sampleRate * this.minAudioDuration * 3;
            if (!this.playing && this.queue.length < minSamples) {
                await this.getQueue(minSamples);
            }
            this.playing = true;
            while (this.playing && this.queue.length) {
                // Create new audio buffer
                const minPlaySamples = Math.min(this.queue.length, this.sampleRate);
                const currentSamples = this.queue.splice(0, minPlaySamples);

                const audioBuffer = this.audioContext.createBuffer(this.channels, currentSamples.length, this.sampleRate);
                audioBuffer.copyToChannel(new Float32Array(currentSamples), 0);

                // Create audio source
                this.source = this.audioContext.createBufferSource();
                this.source.buffer = audioBuffer;

                // Create gain node for smooth transition
                const gainNode = this.audioContext.createGain();

                // Apply fade in/out effect to avoid popping
                const fadeDuration = 0.02; // 20 milliseconds
                gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(1, this.audioContext.currentTime + fadeDuration);

                const duration = audioBuffer.duration;
                if (duration > fadeDuration * 2) {
                    gainNode.gain.setValueAtTime(1, this.audioContext.currentTime + duration - fadeDuration);
                    gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + duration);
                }

                // Connect nodes and start playing
                this.source.connect(gainNode);
                gainNode.connect(this.audioContext.destination);

                this.lastPlayTime = this.audioContext.currentTime;
                log(`Starting playback of ${currentSamples.length} samples, about ${(currentSamples.length / this.sampleRate).toFixed(2)} seconds`, 'info');
                this.source.start();
            }
            await this.getQueue(minSamples);
        }
    }
}

// Factory function to create streamingContext instance
export function createStreamingContext(opusDecoder, audioContext, sampleRate, channels, minAudioDuration) {
    return new StreamingContext(opusDecoder, audioContext, sampleRate, channels, minAudioDuration);
}