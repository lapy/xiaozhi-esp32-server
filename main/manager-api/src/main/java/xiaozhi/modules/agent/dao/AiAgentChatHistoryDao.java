package xiaozhi.modules.agent.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.agent.entity.AgentChatHistoryEntity;

/**
 * {@link AgentChatHistoryEntity} Agent chat history record Dao object
 *
 * @author Goody
 * @version 1.0, 2025/4/30
 * @since 1.0.0
 */
@Mapper
public interface AiAgentChatHistoryDao extends BaseMapper<AgentChatHistoryEntity> {
    /**
     * Delete audio by agent ID
     *
     * @param agentId Agent ID
     */
    void deleteAudioByAgentId(String agentId);

    /**
     * Delete chat history records by agent ID
     *
     * @param agentId Agent ID
     */
    void deleteHistoryByAgentId(String agentId);

    /**
     * Delete audio by agent IDID
     *
     * @param agentId Agent ID
     */
    void deleteAudioIdByAgentId(String agentId);
}
