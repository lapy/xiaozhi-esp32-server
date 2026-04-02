package xiaozhi.modules.llm.service;

/**
 * LLM service interface.
 * Supports multiple large-model backends.
 */
public interface LLMService {

    /**
     * Generate a chat-history summary.
     *
     * @param conversation   conversation content
     * @param promptTemplate prompt template
     * @return summary result
     */
    String generateSummary(String conversation, String promptTemplate);

    /**
     * Generate a chat-history summary using the default prompt template.
     *
     * @param conversation conversation content
     * @return summary result
     */
    String generateSummary(String conversation);

    /**
     * Generate a chat-history summary with a specific model ID.
     *
     * @param conversation conversation content
     * @param modelId      model ID
     * @return summary result
     */
    String generateSummaryWithModel(String conversation, String modelId);

    /**
     * Generate a chat-history summary with a specific model ID and prompt template.
     *
     * @param conversation   conversation content
     * @param promptTemplate prompt template
     * @param modelId        model ID
     * @return summary result
     */
    String generateSummary(String conversation, String promptTemplate, String modelId);

    /**
     * Generate a chat-history summary with historical memory merging.
     *
     * @param conversation   conversation content
     * @param historyMemory  historical memory
     * @param promptTemplate prompt template
     * @param modelId        model ID
     * @return summary result
     */
    String generateSummaryWithHistory(String conversation, String historyMemory, String promptTemplate, String modelId);

    /**
     * Check whether the service is available.
     *
     * @return whether the service is available
     */
    boolean isAvailable();

    /**
     * Check whether the service is available for the specified model.
     *
     * @param modelId model ID
     * @return whether the service is available
     */
    boolean isAvailable(String modelId);
}
