package xiaozhi.modules.agent.service;

import java.util.List;

import com.baomidou.mybatisplus.extension.service.IService;

import xiaozhi.modules.agent.entity.AgentPluginMapping;

/**
 * @description Database operation Service for table [ai_agent_plugin_mapping(unique mapping table between Agent and plugins)]
 * @createDate 2025-05-25 22:33:17
 */
public interface AgentPluginMappingService extends IService<AgentPluginMapping> {

    /**
     * Get plugin parameters by agent id
     * 
     * @param agentId
     * @return
     */
    List<AgentPluginMapping> agentPluginParamsByAgentId(String agentId);

    /**
     * Delete plugin parameters by agent id
     * 
     * @param agentId
     */
    void deleteByAgentId(String agentId);
}
