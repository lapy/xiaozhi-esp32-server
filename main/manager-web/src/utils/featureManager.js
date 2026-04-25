// Feature configuration helper
import Api from "@/apis/api";
import store from "@/store";

class FeatureManager {
    constructor() {
        this.defaultFeatures = {
            voiceprintRecognition: {
                name: 'feature.voiceprintRecognition.name',
                enabled: false,
                description: 'feature.voiceprintRecognition.description'
            },
            voiceClone: {
                name: 'feature.voiceClone.name',
                enabled: false,
                description: 'feature.voiceClone.description'
            },
            knowledgeBase: {
                name: 'feature.knowledgeBase.name',
                enabled: false,
                description: 'feature.knowledgeBase.description'
            },
            mcpAccessPoint: {
                name: 'feature.mcpAccessPoint.name',
                enabled: false,
                description: 'feature.mcpAccessPoint.description'
            },
            vad: {
                name: 'feature.vad.name',
                enabled: false,
                description: 'feature.vad.description'
            },
            asr: {
                name: 'feature.asr.name',
                enabled: false,
                description: 'feature.asr.description'
            }
        };
        this.currentFeatures = { ...this.defaultFeatures }; // Current in-memory configuration
        this.initialized = false;
        this.initPromise = null;
    }

    /**
     * Wait until initialization completes.
     */
    async waitForInitialization() {
        if (!this.initPromise) {
            this.initPromise = this.init();
        }
        await this.initPromise;
        return this.initialized;
    }

    /**
     * Initialize feature configuration.
     */
    async init() {
        try {
            // Fetch configuration from the pub-config endpoint.
            const config = await this.getConfigFromPubConfig();
            if (config) {
                this.currentFeatures = { ...config }; // Persist in memory
                this.initialized = true;
                return;
            }
        } catch (error) {
            console.warn('Failed to fetch configuration from pub-config:', error);
        }

        // Fall back to defaults when the pub-config request fails.
        this.currentFeatures = { ...this.defaultFeatures }; // Persist default configuration in memory
        this.initialized = true;
    }

    /**
     * Update the config cache.
     */
    updateConfigCache(config) {
        store.commit('setPubConfig', config);
        localStorage.setItem('pubConfig', JSON.stringify(config));
    }

    /**
     * Fetch configuration from the pub-config endpoint.
     */
    async getConfigFromPubConfig() {
        return new Promise((resolve) => {
            // Request config directly from pub-config.
            Api.user.getPubConfig((result) => {
                // Validate the response structure.
                if (result && result.status === 200) {
                    // Check for a data field.
                    if (result.data) {
                        const configCache = result.data.data || {};
                        // If a code field is present, validate against it.
                        if (result.data.code !== undefined) {
                            if (result.data.code === 0 && result.data.data && result.data.data.systemWebMenu) {
                                try {
                                    let config;
                                    if (typeof result.data.data.systemWebMenu === 'string') {
                                        // Parse JSON when the payload is serialized.
                                        config = JSON.parse(result.data.data.systemWebMenu);
                                    } else {
                                        // Use the object directly when already parsed.
                                        config = result.data.data.systemWebMenu;
                                    }

                                    // Ensure the configuration contains a features object.
                                    if (config && config.features) {
                                        // Ensure the knowledgeBase feature exists and is configured.
                                        if (!config.features.knowledgeBase) {
                                            console.warn('knowledgeBase is missing from config; merging defaults.');
                                            config.features = { ...this.defaultFeatures, ...config.features };
                                        }
                                        resolve(config.features);
                                    } else {
                                        console.warn('Missing features object in config; using defaults.');
                                        resolve(this.defaultFeatures);
                                    }
                                    configCache.systemWebMenu = config;
                                } catch (error) {
                                    console.warn('Failed to process systemWebMenu config:', error);
                                    resolve(null);
                                }
                            } else {
                                console.warn('pub-config returned a non-zero code or incomplete data; using defaults.');
                                resolve(null);
                            }
                        } else {
                            // Without a code field, check systemWebMenu directly.
                            if (result.data && result.data.systemWebMenu) {
                                try {
                                    let config;
                                    if (typeof result.data.systemWebMenu === 'string') {
                                        // Parse JSON when the payload is serialized.
                                        config = JSON.parse(result.data.systemWebMenu);
                                    } else {
                                        // Use the object directly when already parsed.
                                        config = result.data.systemWebMenu;
                                    }

                                    // Ensure the configuration contains a features object.
                                    if (config && config.features) {
                                        // Ensure the knowledgeBase feature exists and is configured.
                                        if (!config.features.knowledgeBase) {
                                            console.warn('knowledgeBase is missing from config; merging defaults.');
                                            config.features = { ...this.defaultFeatures, ...config.features };
                                        }
                                        resolve(config.features);
                                    } else {
                                        console.warn('Missing features object in config; using defaults.');
                                        resolve(this.defaultFeatures);
                                    }
                                    configCache.systemWebMenu = config;
                                } catch (error) {
                                    console.warn('Failed to process systemWebMenu config:', error);
                                    resolve(null);
                                }
                            } else {
                                console.warn('pub-config response is missing systemWebMenu; using defaults.');
                                resolve(null);
                            }
                        }
                        this.updateConfigCache(configCache)
                    } else {
                        console.warn('pub-config response is missing the data field; using defaults.');
                        resolve(null);
                    }
                } else {
                    console.warn('pub-config request failed; using defaults.');
                    resolve(null);
                }
            });
        });
    }

    /**
     * Get the current configuration.
     */
    getCurrentConfig() {
        // Return the in-memory configuration.
        return this.currentFeatures;
    }

    /**
     * Save configuration to the backend API.
     */
    async saveConfig(config) {
        try {
            // Update the in-memory configuration.
            this.currentFeatures = { ...config };

            // Persist asynchronously to the backend API.
            this.saveConfigToAPI(config).catch(error => {
                console.warn('Failed to save configuration to the API:', error);
            }).finally(() => {
                this.init()
            });

            // Emit a configuration change event.
            window.dispatchEvent(new CustomEvent('featureConfigChanged', {
                detail: config
            }));
        } catch (error) {
            console.error('Failed to save feature configuration:', error);
        }
    }

    /**
     * Save configuration to the backend API.
     */
    async saveConfigToAPI(config) {
        return new Promise((resolve) => {
            // Update the parameter using the known ID (600).
            Api.admin.updateParam(
                {
                    id: 600,
                    paramCode: 'system-web.menu',
                    paramValue: JSON.stringify({
                        features: config,
                        groups: {
                            featureManagement: ["voiceprintRecognition", "voiceClone", "knowledgeBase", "mcpAccessPoint"],
                            voiceManagement: ["vad", "asr"]
                        }
                    }),
                    valueType: 'json',
                    remark: 'System feature menu configuration'
                },
                (updateResult) => {
                    if (updateResult.code === 0) {
                        resolve();
                    } else {
                        // Keep local persistence even if the remote update fails.
                        console.warn('Failed to update the remote parameter:', updateResult.msg);
                        resolve(); // Do not block localStorage persistence
                    }
                },
                (error) => {
                    console.warn('Failed to update the remote parameter:', error);
                    resolve(); // Do not block localStorage persistence
                }
            );
        });
    }



    /**
     * Get all feature configuration.
     */
    getAllFeatures() {
        return this.getCurrentConfig();
    }

    /**
     * Get a simplified configuration object for home-page components.
     */
    getConfig() {
        const features = this.getAllFeatures();
        return {
            voiceprintRecognition: features.voiceprintRecognition?.enabled || false,
            voiceClone: features.voiceClone?.enabled || false,
            knowledgeBase: features.knowledgeBase?.enabled || false,
            mcpAccessPoint: features.mcpAccessPoint?.enabled || false,
            vad: features.vad?.enabled || false,
            asr: features.asr?.enabled || false
        };
    }

    /**
     * Get the status of a specific feature.
     */
    getFeatureStatus(featureKey) {
        const features = this.getAllFeatures();
        return features[featureKey]?.enabled || false;
    }

    /**
     * Set a feature state.
     */
    setFeatureStatus(featureKey, enabled) {
        const features = this.getAllFeatures();
        if (features[featureKey]) {
            features[featureKey].enabled = enabled;
            this.saveConfig(features);
            return true;
        }
        return false;
    }

    /**
     * Enable a feature.
     */
    enableFeature(featureKey) {
        return this.setFeatureStatus(featureKey, true);
    }

    /**
     * Disable a feature.
     */
    disableFeature(featureKey) {
        return this.setFeatureStatus(featureKey, false);
    }

    /**
     * Toggle a feature state.
     */
    toggleFeature(featureKey) {
        const currentStatus = this.getFeatureStatus(featureKey);
        return this.setFeatureStatus(featureKey, !currentStatus);
    }

    /**
     * Reset all features to their default state.
     */
    resetToDefault() {
        this.saveConfig(this.defaultFeatures);
    }

    /**
     * Batch-update feature states.
     */
    updateFeatures(featureUpdates) {
        const features = this.getAllFeatures();
        Object.keys(featureUpdates).forEach(featureKey => {
            if (features[featureKey]) {
                features[featureKey].enabled = featureUpdates[featureKey];
            }
        });
        this.saveConfig(features);
    }

    /**
     * Get the list of enabled features.
     */
    getEnabledFeatures() {
        const features = this.getAllFeatures();
        return Object.keys(features).filter(key => features[key].enabled);
    }

    /**
     * Check whether a feature is enabled.
     */
    isFeatureEnabled(featureKey) {
        return this.getFeatureStatus(featureKey);
    }
}

// Create the singleton instance
const featureManager = new FeatureManager();

export default featureManager;
