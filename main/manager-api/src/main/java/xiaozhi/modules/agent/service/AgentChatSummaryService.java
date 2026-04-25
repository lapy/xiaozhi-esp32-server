package xiaozhi.modules.agent.service;

/**
 * Agent chat-summary service interface.
 */
public interface AgentChatSummaryService {

    /**
     * Generate a chat summary by session ID and save it to agent memory.
     *
     * @param sessionId session ID
     * @return save result
     */
    boolean generateAndSaveChatSummary(String sessionId);

    /**
     * Generate and save a chat title by session ID.
     *
     * @param sessionId session ID
     * @return whether generation succeeded
     */
    boolean generateAndSaveChatTitle(String sessionId);
}
