package xiaozhi.modules.agent.entity;

import java.io.Serializable;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Unique mapping table between Agent and plugins
 * 
 * @TableName ai_agent_plugin_mapping
 */
@Data
@TableName(value = "ai_agent_plugin_mapping")
@Schema(description = "Unique mapping table between Agent and plugins")
public class AgentPluginMapping implements Serializable {
    /**
     * Primary key
     */
    @TableId(type = IdType.ASSIGN_ID)
    @Schema(description = "Mapping information primary key ID")
    private Long id;

    /**
     * Agent ID
     */
    @Schema(description = "Agent ID")
    private String agentId;

    /**
     * Plugin ID
     */
    @Schema(description = "Plugin ID")
    private String pluginId;

    /**
     * Plugin parameters (JSON format)
     */
    @Schema(description = "Plugin parameters (JSON format)")
    private String paramInfo;

    // Redundant field for convenience when querying plugins by id, to find the plugin's Provider_code, see dao layer xml file
    @TableField(exist = false)
    @Schema(description = "Plugin provider_code, corresponds to table ai_model_provider")
    private String providerCode;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;
}