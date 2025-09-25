package xiaozhi.modules.agent.service.biz;

import xiaozhi.modules.agent.dto.AgentChatHistoryReportDTO;

/**
 * Agent chat history business logic layer
 *
 * @author Goody
 * @version 1.0, 2025/4/30
 * @since 1.0.0
 */
public interface AgentChatHistoryBizService {

    /**
     * Chat report method
     *
     * @param agentChatHistoryReportDTO Input object containing information required for chat report
     *                                  For example: device MAC address, file type, content, etc.
     * @return Upload result, true means success, false means failure
     */
    Boolean report(AgentChatHistoryReportDTO agentChatHistoryReportDTO);
}
