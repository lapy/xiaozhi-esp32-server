package xiaozhi.modules.agent.service;

import java.util.List;
import java.util.Map;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.agent.dto.AgentCreateDTO;
import xiaozhi.modules.agent.dto.AgentDTO;
import xiaozhi.modules.agent.dto.AgentUpdateDTO;
import xiaozhi.modules.agent.entity.AgentEntity;
import xiaozhi.modules.agent.vo.AgentInfoVO;

/**
 * Agent table processing service
 *
 * @author Goody
 * @version 1.0, 2025/4/30
 * @since 1.0.0
 */
public interface AgentService extends BaseService<AgentEntity> {
    /**
     * Get admin agent list
     *
     * @param params Query parameters
     * @return Paginated data
     */
    PageData<AgentEntity> adminAgentList(Map<String, Object> params);

    /**
     * Get agent by ID
     *
     * @param id Agent ID
     * @return Agent entity
     */
    AgentInfoVO getAgentById(String id);

    /**
     * Insert agent
     *
     * @param entity Agent entity
     * @return Whether successful
     */
    boolean insert(AgentEntity entity);

    /**
     * Delete agent by user ID
     *
     * @param userId User ID
     */
    void deleteAgentByUserId(Long userId);

    /**
     * Get user agent list
     *
     * @param userId User ID
     * @return Agent list
     */
    List<AgentDTO> getUserAgents(Long userId);

    /**
     * Get device count by agent ID
     *
     * @param agentId Agent ID
     * @return Device count
     */
    Integer getDeviceCountByAgentId(String agentId);

    /**
     * Query default agent information for device by MAC address
     *
     * @param macAddress Device MAC address
     * @return Default agent information, returns null if not exists
     */
    AgentEntity getDefaultAgentByMacAddress(String macAddress);

    /**
     * Check if user has permission to access agent
     *
     * @param agentId Agent ID
     * @param userId  User ID
     * @return Whether has permission
     */
    boolean checkAgentPermission(String agentId, Long userId);

    /**
     * Update agent
     *
     * @param agentId Agent ID
     * @param dto     Information required for updating agent
     */
    void updateAgentById(String agentId, AgentUpdateDTO dto);

    /**
     * Create agent
     *
     * @param dto Information required for creating agent
     * @return Created agent ID
     */
    String createAgent(AgentCreateDTO dto);
}
