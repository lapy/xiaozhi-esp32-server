package xiaozhi.modules.agent.vo;

import lombok.Data;

import java.util.Date;

/**
 * VO for displaying agent voiceprint list
 */
@Data
public class AgentVoicePrintVO {

    /**
     * Primary key id
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
    /**
     * Creation time
     */
    private Date createDate;
}
