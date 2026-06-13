package xiaozhi.modules.agent.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Agent creation DTO
 * Specifically for creating new agents, does not include id, agentCode and sort fields, these fields are automatically generated/set to default values by the system
 */
@Data
@Schema(description = "Agent creation object")
public class AgentCreateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Agent name", example = "Customer Service Assistant")
    @NotBlank(message = "Agent name cannot be empty")
    private String agentName;
}