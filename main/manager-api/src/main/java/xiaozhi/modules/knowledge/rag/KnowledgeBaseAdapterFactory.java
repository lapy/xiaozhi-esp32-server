package xiaozhi.modules.knowledge.rag;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;

/**
 * Factory for knowledge-base adapters.
 * Responsible for creating and managing different knowledge-base API adapter types.
 */
@Slf4j
public class KnowledgeBaseAdapterFactory {

    // Registered adapter type mapping.
    private static final Map<String, Class<? extends KnowledgeBaseAdapter>> adapterRegistry = new HashMap<>();

    // Adapter instance cache.
    private static final Map<String, KnowledgeBaseAdapter> adapterCache = new ConcurrentHashMap<>();

    // Maximum cache size to guard against memory leaks (Issue 9).
    private static final int MAX_CACHE_SIZE = 50;

    static {
        // Register built-in adapter types.
        registerAdapter("ragflow", xiaozhi.modules.knowledge.rag.impl.RAGFlowAdapter.class);
        // Additional adapter types can be registered here later.
    }

    /**
     * Register a new adapter type.
     * 
     * @param adapterType adapter type identifier
     * @param adapterClass adapter class
     */
    public static void registerAdapter(String adapterType, Class<? extends KnowledgeBaseAdapter> adapterClass) {
        if (adapterRegistry.containsKey(adapterType)) {
            log.warn("Adapter type '{}' already exists and will be overwritten", adapterType);
        }
        adapterRegistry.put(adapterType, adapterClass);
        log.info("Registered adapter type: {} -> {}", adapterType, adapterClass.getSimpleName());
    }

    /**
     * Return an adapter instance.
     * 
     * @param adapterType adapter type
     * @param config configuration values
     * @return adapter instance
     */
    public static KnowledgeBaseAdapter getAdapter(String adapterType, Map<String, Object> config) {
        String cacheKey = buildCacheKey(adapterType, config);

        // Reuse a cached instance when available.
        if (adapterCache.containsKey(cacheKey)) {
            log.debug("Loaded adapter instance from cache: {}", cacheKey);
            return adapterCache.get(cacheKey);
        }

        // Create a new adapter instance.
        KnowledgeBaseAdapter adapter = createAdapter(adapterType, config);

        // Cache the adapter instance with a capacity guard.
        if (adapterCache.size() >= MAX_CACHE_SIZE) {
            log.warn("Adapter cache reached its limit ({}), clearing it as a memory-safety fallback", MAX_CACHE_SIZE);
            // Simple fallback: clear the cache. An LRU strategy would be better in production.
            adapterCache.clear();
        }

        adapterCache.put(cacheKey, adapter);
        log.info("Created and cached adapter instance: {}", cacheKey);

        return adapter;
    }

    /**
     * Return an adapter instance without explicit configuration.
     * 
     * @param adapterType adapter type
     * @return adapter instance
     */
    public static KnowledgeBaseAdapter getAdapter(String adapterType) {
        return getAdapter(adapterType, null);
    }

    /**
     * Return all registered adapter types.
     * 
     * @return registered adapter types
     */
    public static Set<String> getRegisteredAdapterTypes() {
        return adapterRegistry.keySet();
    }

    /**
     * Check whether an adapter type is registered.
     * 
     * @param adapterType adapter type
     * @return whether the adapter type is registered
     */
    public static boolean isAdapterTypeRegistered(String adapterType) {
        return adapterRegistry.containsKey(adapterType);
    }

    /**
     * Clear the adapter cache.
     */
    public static void clearCache() {
        int cacheSize = adapterCache.size();
        adapterCache.clear();
        log.info("Cleared the adapter cache and removed {} instances", cacheSize);
    }

    /**
     * Remove cached instances for a specific adapter type.
     * 
     * @param adapterType adapter type
     */
    public static void removeCacheByType(String adapterType) {
        int removedCount = 0;
        for (String cacheKey : adapterCache.keySet()) {
            if (cacheKey.startsWith(adapterType + "@")) {
                adapterCache.remove(cacheKey);
                removedCount++;
            }
        }
        log.info("Removed {} cached instances for adapter type '{}'", removedCount, adapterType);
    }

    /**
     * Return adapter-factory status information.
     * 
     * @return status information
     */
    public static Map<String, Object> getFactoryStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("registeredAdapterTypes", adapterRegistry.keySet());
        status.put("cachedAdapterCount", adapterCache.size());
        status.put("cacheKeys", adapterCache.keySet());
        return status;
    }

    /**
     * Create an adapter instance.
     * 
     * @param adapterType adapter type
     * @param config configuration values
     * @return adapter instance
     */
    private static KnowledgeBaseAdapter createAdapter(String adapterType, Map<String, Object> config) {
        if (!adapterRegistry.containsKey(adapterType)) {
            throw new RenException(ErrorCode.RAG_ADAPTER_TYPE_NOT_SUPPORTED,
                    "Unsupported adapter type: " + adapterType);
        }

        try {
            Class<? extends KnowledgeBaseAdapter> adapterClass = adapterRegistry.get(adapterType);
            KnowledgeBaseAdapter adapter = adapterClass.getDeclaredConstructor().newInstance();

            // Initialize the adapter.
            if (config != null) {
                adapter.initialize(config);

                // Validate the configuration.
                if (!adapter.validateConfig(config)) {
                    throw new RenException(ErrorCode.RAG_CONFIG_VALIDATION_FAILED,
                            "Adapter configuration validation failed: " + adapterType);
                }
            }

            log.info("Successfully created adapter instance: {}", adapterType);
            return adapter;

        } catch (Exception e) {
            log.error("Failed to create adapter instance: {}", adapterType, e);
            throw new RenException(ErrorCode.RAG_ADAPTER_CREATION_FAILED,
                    "Failed to create adapter: " + adapterType + ", error: " + e.getMessage());
        }
    }

    /**
     * Build the cache key.
     * 
     * @param adapterType adapter type
     * @param config configuration values
     * @return cache key
     */
    private static String buildCacheKey(String adapterType, Map<String, Object> config) {
        if (config == null || config.isEmpty()) {
            return adapterType + "@default";
        }

        // Build the key from the configuration values.
        StringBuilder keyBuilder = new StringBuilder(adapterType + "@");

        // Use the configuration hash as part of the cache key.
        int configHash = config.hashCode();
        keyBuilder.append(configHash);

        return keyBuilder.toString();
    }
}
