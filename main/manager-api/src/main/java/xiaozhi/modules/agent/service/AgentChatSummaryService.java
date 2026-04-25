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
     * 根据会话ID生成聊天标题并保存
     *
     * @param sessionId 会话ID
     * @return 是否成功
     */
    boolean generateAndSaveChatTitle(String sessionId);
}
