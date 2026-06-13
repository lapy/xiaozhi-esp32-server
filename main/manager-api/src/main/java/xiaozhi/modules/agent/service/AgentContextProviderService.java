package xiaozhi.modules.agent.service;

import xiaozhi.common.service.BaseService;
import xiaozhi.modules.agent.entity.AgentContextProviderEntity;

public interface AgentContextProviderService extends BaseService<AgentContextProviderEntity> {
    /**
     * Get context-provider configuration by agent ID.
     *
     * @param agentId agent ID
     * @return context-provider configuration entity
     */
    AgentContextProviderEntity getByAgentId(String agentId);

    /**
     * Save or update context-provider configuration.
     *
     * @param entity entity to persist
     */
    void saveOrUpdateByAgentId(AgentContextProviderEntity entity);

    /**
     * Delete context-provider configuration by agent ID.
     *
     * @param agentId agent ID
     */
    void deleteByAgentId(String agentId);
}
