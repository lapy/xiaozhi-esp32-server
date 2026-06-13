/**
 * Live2D manager.
 * Handles model initialization, mouth animation, and interaction behavior.
 */
class Live2DManager {
    constructor() {
        this.live2dApp = null;
        this.live2dModel = null;
        this.isTalking = false;
        this.mouthAnimationId = null;
        this.mouthParam = 'ParamMouthOpenY';
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.lastEmotionActionTime = null;
        this.currentModelName = null;

        // Model-specific configuration.
        this.modelConfig = {
            'hiyori_pro_zh': {
                mouthParam: 'ParamMouthOpenY',
                mouthAmplitude: 1.0,
                mouthThresholds: { low: 0.3, high: 0.7 },
                motionMap: {
                    'FlickUp': 'FlickUp',
                    'FlickDown': 'FlickDown',
                    'Tap': 'Tap',
                    'Tap@Body': 'Tap@Body',
                    'Flick': 'Flick',
                    'Flick@Body': 'Flick@Body'
                }
            },
            'natori_pro_zh': {
                mouthParam: 'ParamMouthOpenY',
                mouthAmplitude: 1.0,
                mouthThresholds: { low: 0.1, high: 0.4 },
                mouthFormParam: 'ParamMouthForm',
                mouthFormAmplitude: 1.0,
                mouthForm2Param: 'ParamMouthForm2',
                mouthForm2Amplitude: 0.8,
                motionMap: {
                    'FlickUp': 'FlickUp',
                    'FlickDown': 'Flick@Body',
                    'Tap': 'Tap',
                    'Tap@Body': 'Tap@Head',
                    'Flick': 'Tap',
                    'Flick@Body': 'Flick@Body'
                }
            }
        };

        // Emotion-to-motion mapping.
        this.emotionToActionMap = {
            'happy': 'FlickUp',      // happy -> upward flick
            'laughing': 'FlickUp',   // laughing -> upward flick
            'funny': 'FlickUp',      // funny -> upward flick
            'sad': 'FlickDown',      // sad -> downward flick
            'crying': 'FlickDown',   // crying -> downward flick
            'angry': 'Tap@Body',     // angry -> body tap
            'surprised': 'Tap',      // surprised -> tap
            'neutral': 'Flick',      // neutral -> flick
            'default': 'Flick@Body'  // default -> body flick
        };

        // Single/double-click detection state.
        this._lastClickTime = 0;
        this._lastClickPos = { x: 0, y: 0 };
        this._singleClickTimer = null;
        this._doubleClickMs = 280; // double-click threshold in ms
        this._doubleClickDist = 16; // max movement allowed for a double click
        // Swipe detection state.
        this._pointerDown = false;
        this._downPos = { x: 0, y: 0 };
        this._downTime = 0;
        this._downArea = 'Body';
        this._movedBeyondClick = false;
        this._swipeMinDist = 24; // minimum distance required to trigger a swipe
    }

    /**
     * Initialize Live2D.
     */
    async initializeLive2D() {
        try {
            const canvas = document.getElementById('live2d-stage');

            // Expose PIXI for the Live2D runtime.
            window.PIXI = PIXI;

            this.live2dApp = new PIXI.Application({
                view: canvas,
                height: window.innerHeight,
                width: window.innerWidth,
                resolution: window.devicePixelRatio,
                autoDensity: true,
                antialias: true,
                backgroundAlpha: 0,
            });

            // Load the Live2D model relative to the current test page path.
            const currentPath = window.location.pathname;
            const lastSlashIndex = currentPath.lastIndexOf('/');
            const basePath = currentPath.substring(0, lastSlashIndex + 1);

            // Restore the last selected model from localStorage.
            const savedModelName = localStorage.getItem('live2dModel') || 'hiyori_pro_zh';
            const modelFileMap = {
                'hiyori_pro_zh': 'hiyori_pro_t11.model3.json',
                'natori_pro_zh': 'natori_pro_t06.model3.json'
            };
            const modelFileName = modelFileMap[savedModelName] || 'hiyori_pro_t11.model3.json';
            const modelPath = basePath + 'resources/' + savedModelName + '/runtime/' + modelFileName;

            this.live2dModel = await PIXI.live2d.Live2DModel.from(modelPath);
            this.live2dApp.stage.addChild(this.live2dModel);

            // Store the current model name.
            this.currentModelName = savedModelName;

            // Sync the model selector.
            const modelSelect = document.getElementById('live2dModelSelect');
            if (modelSelect) {
                modelSelect.value = savedModelName;
            }

            // Apply model-specific mouth parameter names.
            if (this.modelConfig[savedModelName]) {
                this.mouthParam = this.modelConfig[savedModelName].mouthParam || 'ParamMouthOpenY';
            }

            // Configure the model transform.
            this.live2dModel.scale.set(0.33);
            this.live2dModel.x = (window.innerWidth - this.live2dModel.width) * 0.5;
            this.live2dModel.y = -50;

            // Enable interactions and custom hit handling.

            this.live2dModel.interactive = true;


            this.live2dModel.on('doublehit', (args) => {
                const area = Array.isArray(args) ? args[0] : args;

                // Trigger the double-click motion.
                if (area === 'Body') {
                    this.motion('Flick@Body');
                } else if (area === 'Head' || area === 'Face') {
                    this.motion('Flick');
                }

                const app = window.chatApp;
                const payload = JSON.stringify({ type: 'live2d', event: 'doublehit', area });
                if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                    app.dataChannel.send(payload);
                }

            });

            this.live2dModel.on('singlehit', (args) => {
                const area = Array.isArray(args) ? args[0] : args;

                // Trigger the single-click motion.
                if (area === 'Body') {
                    this.motion('Tap@Body');
                } else if (area === 'Head' || area === 'Face') {
                    this.motion('Tap');
                }

                const app = window.chatApp;
                const payload = JSON.stringify({ type: 'live2d', event: 'singlehit', area });
                if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                    app.dataChannel.send(payload);
                }

            });

            this.live2dModel.on('swipe', (args) => {
                const area = Array.isArray(args) ? args[0] : args;
                const dir = Array.isArray(args) ? args[1] : undefined;

                // Trigger swipe motions.
                if (area === 'Body') {
                    if (dir === 'up') {
                        this.motion('FlickUp');
                    } else if (dir === 'down') {
                        this.motion('FlickDown');
                    }
                } else if (area === 'Head' || area === 'Face') {
                    if (dir === 'up') {
                        this.motion('FlickUp');
                    } else if (dir === 'down') {
                        this.motion('FlickDown');
                    }
                }

                const app = window.chatApp;
                const payload = JSON.stringify({ type: 'live2d', event: 'swipe', area, dir });
                if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                    app.dataChannel.send(payload);
                }

            });

            // Fallback custom hit logic for head/body regions plus click/swipe differentiation.
            this.live2dModel.on('pointerdown', (event) => {
                try {
                    const global = event.data.global;
                    const bounds = this.live2dModel.getBounds();
                    // Only continue if the pointer is inside the visible model bounds.
                    if (!bounds || !bounds.contains(global.x, global.y)) return;

                    const relX = (global.x - bounds.x) / (bounds.width || 1);
                    const relY = (global.y - bounds.y) / (bounds.height || 1);
                    let area = '';
                    // Heuristic: treat the upper portion of the visible bounds as head/face.
                    if (relX >= 0.4 && relX <= 0.6) {
                        if (relY <= 0.15) {
                            area = 'Head';
                        } else if (relY <= 0.23) {
                            area = 'Face';
                        } else {
                            area = 'Body';
                        }
                    }
                    if (area === '') {
                        return;
                    }

                    // Record pointer state for swipe detection.
                    this._pointerDown = true;
                    this._downPos = { x: global.x, y: global.y };
                    this._downTime = performance.now();
                    this._downArea = area;
                    this._movedBeyondClick = false;

                    const now = performance.now();
                    const dt = now - (this._lastClickTime || 0);
                    const dx = global.x - (this._lastClickPos?.x || 0);
                    const dy = global.y - (this._lastClickPos?.y || 0);
                    const dist = Math.hypot(dx, dy);

                    // Only perform single/double click detection for confirmed hits.
                    if (this._lastClickTime && dt <= this._doubleClickMs && dist <= this._doubleClickDist) {
                        // Double-click: cancel the pending single-click handler.
                        if (this._singleClickTimer) {
                            clearTimeout(this._singleClickTimer);
                            this._singleClickTimer = null;
                        }
                        if (typeof this.live2dModel.emit === 'function') {
                            this.live2dModel.emit('doublehit', [area]);
                        }
                        this._lastClickTime = 0;
                        this._pointerDown = false; // reset after a double click
                        return;
                    }

                    // Potential single click: record and confirm after the double-click window.
                    this._lastClickTime = now;
                    this._lastClickPos = { x: global.x, y: global.y };
                    if (this._singleClickTimer) {
                        clearTimeout(this._singleClickTimer);
                        this._singleClickTimer = null;
                    }
                    this._singleClickTimer = setTimeout(() => {
                        // If the pointer moved too far, do not treat it as a click.
                        if (!this._movedBeyondClick && typeof this.live2dModel.emit === 'function') {
                            this.live2dModel.emit('singlehit', [area]);
                        }
                        this._singleClickTimer = null;
                        this._lastClickTime = 0;
                    }, this._doubleClickMs);
                } catch (e) {
                    // Ignore fallback hit-testing errors so they do not break the main flow.
                }
            });

            // Pointer move: determine whether the gesture became a swipe.
            this.live2dModel.on('pointermove', (event) => {
                try {
                    if (!this._pointerDown) return;
                    const global = event.data.global;
                    const dx = global.x - this._downPos.x;
                    const dy = global.y - this._downPos.y;
                    const dist = Math.hypot(dx, dy);

                    // Reuse the double-click distance as the click-vs-swipe threshold.
                    if (dist > this._doubleClickDist) {
                        this._movedBeyondClick = true;
                        // Cancel any pending single-click if the pointer moved too far.
                        if (this._singleClickTimer) {
                            clearTimeout(this._singleClickTimer);
                            this._singleClickTimer = null;
                        }
                        this._lastClickTime = 0;
                    }
                } catch (e) {
                    // Ignore pointer-move detection errors.
                }
            });

            // Pointer up: finalize swipe detection.
            const handlePointerUp = (event) => {
                try {
                    if (!this._pointerDown) return;
                    const global = (event && event.data && event.data.global) ? event.data.global : { x: this._downPos.x, y: this._downPos.y };
                    const dx = global.x - this._downPos.x;
                    const dy = global.y - this._downPos.y;
                    const dist = Math.hypot(dx, dy);

                    // Emit a swipe event when the gesture traveled far enough.
                    if (this._movedBeyondClick && dist >= this._swipeMinDist) {
                        if (typeof this.live2dModel.emit === 'function') {
                            const dir = Math.abs(dx) >= Math.abs(dy)
                                ? (dx > 0 ? 'right' : 'left')
                                : (dy > 0 ? 'down' : 'up');
                            this.live2dModel.emit('swipe', [this._downArea, dir]);
                        }
                        // Prevent single/double-click handling after a swipe.
                        if (this._singleClickTimer) {
                            clearTimeout(this._singleClickTimer);
                            this._singleClickTimer = null;
                        }
                        this._lastClickTime = 0;
                    }
                } catch (e) {
                    // Ignore pointer-up detection errors.
                }
                finally {
                    this._pointerDown = false;
                    this._movedBeyondClick = false;
                }
            };

            this.live2dModel.on('pointerup', handlePointerUp);
            this.live2dModel.on('pointerupoutside', handlePointerUp);

            // Keep the model centered when the window size changes.
            window.addEventListener('resize', () => {
                if (this.live2dModel) {
                    // Recompute the model position from the current window dimensions.
                    this.live2dModel.x = (window.innerWidth - this.live2dModel.width) * 0.5;
                    this.live2dModel.y = -50;
                }
            });

        } catch (err) {
            console.error('Failed to load the Live2D model:', err);
        }
    }

    /**
     * Initialize the audio analyzer used by the player pipeline.
     */
    initializeAudioAnalyzer() {
        try {
            // Get the audio player instance.
            const audioPlayer = window.chatApp?.audioPlayer;
            if (!audioPlayer) {
                console.warn('The audio player is not initialized, so the analyzer is unavailable.');
                return false;
            }

            // Get the player audio context.
            this.audioContext = audioPlayer.getAudioContext();
            if (!this.audioContext) {
                console.warn('Could not get the audio player context.');
                return false;
            }

            // Create the analyzer node.
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

            return true;
        } catch (error) {
            console.error('Failed to initialize the audio analyzer:', error);
            return false;
        }
    }

    /**
     * Connect to the audio player output.
     */
    connectToAudioPlayer() {
        try {
            // Get the audio player streaming context.
            const audioPlayer = window.chatApp?.audioPlayer;
            if (!audioPlayer || !audioPlayer.streamingContext) {
                console.warn('The audio player or streaming context is not initialized.');
                return false;
            }

            // Use the player streaming context.
            const streamingContext = audioPlayer.streamingContext;

            // Reuse the analyzer node created by the player.
            const analyser = streamingContext.getAnalyser();
            if (!analyser) {
                console.warn('The audio player has not created an analyzer node yet.');
                return false;
            }

            // Use the player-owned analyzer.
            this.analyser = analyser;
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            return true;
        } catch (error) {
            console.error('Failed to connect to the audio player:', error);
            return false;
        }
    }

    /**
     * Mouth animation loop.
     */
    animateMouth() {
        if (!this.isTalking) return;
        if (!this.live2dModel) return;
        const internal = this.live2dModel && this.live2dModel.internalModel;
        if (internal && internal.coreModel) {
            const coreModel = internal.coreModel;

            let mouthOpenY = 0;
            let mouthForm = 0;
            let mouthForm2 = 0;
            let average = 0;

            if (this.analyser && this.dataArray) {
                this.analyser.getByteFrequencyData(this.dataArray);
                average = this.dataArray.reduce((a, b) => a + b) / this.dataArray.length;

                const normalizedVolume = average / 255;

                // Read model-specific thresholds.
                let lowThreshold = 0.3;
                let highThreshold = 0.7;
                if (this.currentModelName && this.modelConfig[this.currentModelName]) {
                    lowThreshold = this.modelConfig[this.currentModelName].mouthThresholds?.low || 0.3;
                    highThreshold = this.modelConfig[this.currentModelName].mouthThresholds?.high || 0.7;
                }

                // Map volume using model-specific thresholds.
                let minOpenY = 0.1;
                if (this.currentModelName && this.modelConfig[this.currentModelName]) {
                    minOpenY = this.modelConfig[this.currentModelName].mouthMinOpenY || 0.1;
                }

                if (normalizedVolume < lowThreshold) {
                    mouthOpenY = minOpenY + Math.pow(normalizedVolume / lowThreshold, 1.5) * (0.4 - minOpenY);
                } else if (normalizedVolume < highThreshold) {
                    mouthOpenY = 0.4 + (normalizedVolume - lowThreshold) / (highThreshold - lowThreshold) * 0.4;
                } else {
                    mouthOpenY = 0.8 + Math.pow((normalizedVolume - highThreshold) / (1 - highThreshold), 1.2) * 0.2;
                }

                // Apply model-specific mouth amplitude.
                let amplitudeMultiplier = 1.0;
                let maxOpenY = 2.5;
                if (this.currentModelName && this.modelConfig[this.currentModelName]) {
                    amplitudeMultiplier = this.modelConfig[this.currentModelName].mouthAmplitude;
                    maxOpenY = this.modelConfig[this.currentModelName].maxOpenY || 2.5;
                }
                mouthOpenY = mouthOpenY * amplitudeMultiplier;
                mouthOpenY = Math.min(Math.max(mouthOpenY, 0), maxOpenY);

                // Compute mouth shape parameters for models that support them.
                if (this.currentModelName && this.modelConfig[this.currentModelName]?.mouthFormParam) {
                    const config = this.modelConfig[this.currentModelName];
                    const formAmplitude = config.mouthFormAmplitude || 0.5;
                    const form2Amplitude = config.mouthForm2Amplitude || 0;

                    // Adjust mouth shape from flatter to rounder as volume increases.
                    mouthForm = (normalizedVolume - 0.5) * 2 * formAmplitude;
                    mouthForm = Math.max(-formAmplitude, Math.min(formAmplitude, mouthForm));

                    // Secondary mouth-shape parameter used by natori.
                    if (config.mouthForm2Param) {
                        mouthForm2 = (normalizedVolume - 0.3) * 2 * form2Amplitude;
                        mouthForm2 = Math.max(-form2Amplitude, Math.min(form2Amplitude, mouthForm2));
                    }
                }

                // Debug log for current mouth parameters.
                console.log(`[Live2D] Model: ${this.currentModelName || 'unknown'}, Volume: ${average?.toFixed(0)}, OpenY: ${mouthOpenY.toFixed(3)}, Form: ${mouthForm.toFixed(3)}, Form2: ${mouthForm2.toFixed(3)}`);
            }

            // Set the mouth opening parameter.
            coreModel.setParameterValueById(this.mouthParam, mouthOpenY);

            // Set mouth-shape parameters when supported by the model.
            if (this.currentModelName && this.modelConfig[this.currentModelName]?.mouthFormParam) {
                const config = this.modelConfig[this.currentModelName];
                const formParam = config.mouthFormParam;
                coreModel.setParameterValueById(formParam, mouthForm);

                // Set the secondary mouth-shape parameter for natori.
                if (config.mouthForm2Param) {
                    coreModel.setParameterValueById(config.mouthForm2Param, mouthForm2);
                }
            }

            coreModel.update();
        }
        this.mouthAnimationId = requestAnimationFrame(() => this.animateMouth());
    }

    /**
     * Start the talking animation.
     */
    startTalking() {
        if (this.isTalking || !this.live2dModel) return;

        // Ensure the audio analyzer is ready.
        if (!this.analyser) {
            if (!this.initializeAudioAnalyzer()) {
                console.warn('Audio analyzer initialization failed. Falling back to simulated animation.');
                // Even without the analyzer, keep the mouth animation running.
                this.isTalking = true;
                this.animateMouth();
                return;
            }
        }

        // Connect to the audio player output.
        if (!this.connectToAudioPlayer()) {
            console.warn('Could not connect to the audio player output. Falling back to simulated animation.');
        }

        this.isTalking = true;
        this.animateMouth();
    }

    /**
     * Stop the talking animation.
     */
    stopTalking() {
        this.isTalking = false;
        if (this.mouthAnimationId) {
            cancelAnimationFrame(this.mouthAnimationId);
            this.mouthAnimationId = null;
        }

        // Reset mouth parameters.
        if (this.live2dModel) {
            const internal = this.live2dModel.internalModel;
            if (internal && internal.coreModel) {
                const coreModel = internal.coreModel;
                coreModel.setParameterValueById(this.mouthParam, 0);
                coreModel.update();
            }
        }
    }

    /**
     * Trigger a motion based on emotion.
     * @param {string} emotion - Emotion name.
     */
    triggerEmotionAction(emotion) {
        if (!this.live2dModel) return;

        // Rate-limit emotion-triggered motions.
        const now = Date.now();
        if (this.lastEmotionActionTime && now - this.lastEmotionActionTime < 5000) { // 5-second cooldown
            return;
        }

        // Resolve the matching action.
        const action = this.emotionToActionMap[emotion] || this.emotionToActionMap['default'];

        // Trigger the action and remember the timestamp.
        this.motion(action);
        this.lastEmotionActionTime = now;
    }



    /**
     * Trigger a Live2D motion.
     * @param {string} name - Motion group name such as 'TapBody', 'FlickUp', or 'Idle'.
     */
    motion(name) {
        try {
            if (!this.live2dModel) return;

            // Resolve model-specific motion name mappings.
            let actualMotionName = name;
            if (this.currentModelName && this.modelConfig[this.currentModelName]) {
                const motionMap = this.modelConfig[this.currentModelName].motionMap;
                actualMotionName = motionMap[name] || name;
            }

            this.live2dModel.motion(actualMotionName);
        } catch (error) {
            console.error('Failed to trigger the motion:', error);
        }
    }

    /**
     * Register model interaction handlers.
     */
    setupModelInteractions() {
        if (!this.live2dModel) return;

        this.live2dModel.interactive = true;

        this.live2dModel.on('doublehit', (args) => {
            const area = Array.isArray(args) ? args[0] : args;

            if (area === 'Body') {
                this.motion('Flick@Body');
            } else if (area === 'Head' || area === 'Face') {
                this.motion('Flick');
            }

            const app = window.chatApp;
            const payload = JSON.stringify({ type: 'live2d', event: 'doublehit', area });
            if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                app.dataChannel.send(payload);
            }
        });

        this.live2dModel.on('singlehit', (args) => {
            const area = Array.isArray(args) ? args[0] : args;

            if (area === 'Body') {
                this.motion('Tap@Body');
            } else if (area === 'Head' || area === 'Face') {
                this.motion('Tap');
            }

            const app = window.chatApp;
            const payload = JSON.stringify({ type: 'live2d', event: 'singlehit', area });
            if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                app.dataChannel.send(payload);
            }
        });

        this.live2dModel.on('swipe', (args) => {
            const area = Array.isArray(args) ? args[0] : args;
            const dir = Array.isArray(args) ? args[1] : undefined;

            if (area === 'Body') {
                if (dir === 'up') {
                    this.motion('FlickUp');
                } else if (dir === 'down') {
                    this.motion('FlickDown');
                }
            }

            const app = window.chatApp;
            const payload = JSON.stringify({ type: 'live2d', event: 'swipe', area, dir });
            if (app && app.dataChannel && app.dataChannel.readyState === 'open') {
                app.dataChannel.send(payload);
            }
        });

        this.live2dModel.on('pointerdown', (event) => {
            try {
                const global = event.data.global;
                const bounds = this.live2dModel.getBounds();
                if (!bounds || !bounds.contains(global.x, global.y)) return;

                const relX = (global.x - bounds.x) / (bounds.width || 1);
                const relY = (global.y - bounds.y) / (bounds.height || 1);
                let area = '';

                if (relX >= 0.4 && relX <= 0.6) {
                    if (relY <= 0.15) {
                        area = 'Head';
                    } else if (relY >= 0.7) {
                        area = 'Body';
                    }
                }

                if (!area) return;

                const now = Date.now();
                const dt = now - (this._lastClickTime || 0);
                const dx = global.x - (this._lastClickPos?.x || 0);
                const dy = global.y - (this._lastClickPos?.y || 0);
                const dist = Math.hypot(dx, dy);

                if (this._lastClickTime && dt <= this._doubleClickMs && dist <= this._doubleClickDist) {
                    if (this._singleClickTimer) {
                        clearTimeout(this._singleClickTimer);
                        this._singleClickTimer = null;
                    }

                    this.live2dModel.emit('doublehit', area);
                    this._lastClickTime = null;
                    this._lastClickPos = null;
                } else {
                    this._lastClickTime = now;
                    this._lastClickPos = { x: global.x, y: global.y };

                    this._singleClickTimer = setTimeout(() => {
                        this._singleClickTimer = null;
                        this.live2dModel.emit('singlehit', area);
                    }, this._doubleClickMs);
                }
            } catch (e) {
                console.warn('pointerdown handler error:', e);
            }
        });
    }

    /**
     * Clean up allocated resources.
     */
    destroy() {
        this.stopTalking();

        // Clean up the audio analyzer.
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        this.analyser = null;
        this.dataArray = null;

        // Destroy the Live2D app.
        if (this.live2dApp) {
            this.live2dApp.destroy(true);
            this.live2dApp = null;
        }
        this.live2dModel = null;
    }

    /**
     * Switch the active Live2D model.
     * @param {string} modelName - Model directory name such as 'hiyori_pro_zh' or 'natori_pro_zh'.
     * @returns {Promise<boolean>} Whether the switch succeeded.
     */
    async switchModel(modelName) {
        try {
            // Map model directory names to model files.
            const modelFileMap = {
                'hiyori_pro_zh': 'hiyori_pro_t11.model3.json',
                'natori_pro_zh': 'natori_pro_t06.model3.json',
                'chitose': 'chitose.model3.json',
                'haru_greeter_pro_jp': 'haru_greeter_t05.model3.json'
            };

            const modelFileName = modelFileMap[modelName];
            if (!modelFileName) {
                console.error('Unknown model name:', modelName);
                return false;
            }

            // Resolve the base path.
            const currentPath = window.location.pathname;
            const lastSlashIndex = currentPath.lastIndexOf('/');
            const basePath = currentPath.substring(0, lastSlashIndex + 1);
            const modelPath = basePath + 'resources/' + modelName + '/runtime/' + modelFileName;

            // Remove the existing model first.
            if (this.live2dModel) {
                this.live2dApp.stage.removeChild(this.live2dModel);
                this.live2dModel.destroy();
                this.live2dModel = null;
            }

            // Show the loading indicator.
            const app = window.chatApp;
            if (app) {
                app.setModelLoadingStatus(true);
            }

            // Load the new model.
            this.live2dModel = await PIXI.live2d.Live2DModel.from(modelPath);
            this.live2dApp.stage.addChild(this.live2dModel);

            // Configure model transform.
            this.live2dModel.scale.set(0.33);
            this.live2dModel.x = (window.innerWidth - this.live2dModel.width) * 0.5;
            this.live2dModel.y = -50;

            // Re-bind model interactions.
            this.setupModelInteractions();

            // Hide the loading indicator.
            if (app) {
                app.setModelLoadingStatus(false);
            }

            // Persist the current model name.
            this.currentModelName = modelName;

            // Apply model-specific mouth parameter names.
            if (this.modelConfig[modelName]) {
                this.mouthParam = this.modelConfig[modelName].mouthParam || 'ParamMouthOpenY';
            }

            // Save the selection to localStorage.
            localStorage.setItem('live2dModel', modelName);

            // Sync the selector.
            const modelSelect = document.getElementById('live2dModelSelect');
            if (modelSelect) {
                modelSelect.value = modelName;
            }

            console.log('Model switched successfully:', modelName);
            return true;
        } catch (error) {
            console.error('Failed to switch the model:', error);
            const app = window.chatApp;
            if (app) {
                app.setModelLoadingStatus(false);
            }
            return false;
        }
    }


}

// Expose the manager globally.
window.Live2DManager = Live2DManager;
