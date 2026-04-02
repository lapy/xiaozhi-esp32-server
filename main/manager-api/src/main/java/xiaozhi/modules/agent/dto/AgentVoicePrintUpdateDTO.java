package xiaozhi.modules.agent.dto;

import lombok.Data;

/**
 * DTO for updating agent voiceprint
 *
 * @author zjy
 */
@Data
public class AgentVoicePrintUpdateDTO {
    /**
     * Agent voiceprint id
     */
    private String id;
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
