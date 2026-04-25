package xiaozhi.modules.config.service;

import java.util.Map;

public interface ConfigService {
    /**
     * Get server configuration
     * 
     * @param isCache Whether to cache
     * @return Configuration information
     */
    Object getConfig(Boolean isCache);

    /**
     * Get agent model configuration
     * 
     * @param macAddress     MAC address
     * @param selectedModule Client instantiated models
     * @return Model configuration information
     */
    Map<String, Object> getAgentModels(String macAddress, Map<String, String> selectedModule);
}