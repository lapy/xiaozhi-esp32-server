package xiaozhi.modules.agent.dto;

import lombok.Data;

/**
 * DTO for saving agent voiceprint
 *
 * @author zjy
 */
@Data
public class AgentVoicePrintSaveDTO {
    /**
     * Associated agent id
     */
    private String agentId;
    /**
     * Audio file id
     */
    private String audioId;
    /**
     * Name of the person whose voiceprint this is from
     */
    private String sourceName;
    /**
     * Description of the person whose voiceprint this is from
     */
    private String introduce;
}
