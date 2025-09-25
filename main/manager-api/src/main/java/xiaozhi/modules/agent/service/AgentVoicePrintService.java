package xiaozhi.modules.agent.service;

import java.util.List;

import xiaozhi.modules.agent.dto.AgentVoicePrintSaveDTO;
import xiaozhi.modules.agent.dto.AgentVoicePrintUpdateDTO;
import xiaozhi.modules.agent.vo.AgentVoicePrintVO;

/**
 * Agent voiceprint processing service
 *
 * @author zjy
 */
public interface AgentVoicePrintService {
    /**
     * Add new voiceprint for agent
     *
     * @param dto Data for saving agent voiceprint
     * @return T: success F: failure
     */
    boolean insert(AgentVoicePrintSaveDTO dto);

    /**
     * Delete specified voiceprint of agent
     *
     * @param userId       Current logged in user id
     * @param voicePrintId Voiceprint id
     * @return Whether successful T: success F: failure
     */
    boolean delete(Long userId, String voicePrintId);

    /**
     * Get all voiceprint data for specified agent
     *
     * @param userId  Current logged in user ID
     * @param agentId Agent ID
     * @return Voiceprint data collection
     */
    List<AgentVoicePrintVO> list(Long userId, String agentId);

    /**
     * Update specified voiceprint data for agent
     *
     * @param userId Current logged in user ID
     * @param dto    Modified voiceprint data
     * @return Whether successful T: success F: failure
     */
    boolean update(Long userId, AgentVoicePrintUpdateDTO dto);

}
