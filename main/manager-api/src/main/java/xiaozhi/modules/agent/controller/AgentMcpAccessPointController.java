package xiaozhi.modules.agent.controller;

import java.util.List;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.agent.service.AgentMcpAccessPointService;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.security.user.SecurityUser;

@Tag(name = "Agent MCP Access Point Management")
@RequiredArgsConstructor
@RestController
@RequestMapping("/agent/mcp")
public class AgentMcpAccessPointController {
    private final AgentMcpAccessPointService agentMcpAccessPointService;
    private final AgentService agentService;

    /**
     * Get agent MCP access point address
     * 
     * @param audioId Agent id
     * @return Return error reminder or MCP access point address
     */
    @Operation(summary = "Get agent MCP access point address")
    @GetMapping("/address/{agentId}")
    @RequiresPermissions("sys:role:normal")
    public Result<String> getAgentMcpAccessAddress(@PathVariable("agentId") String agentId) {
        // Get current user
        UserDetail user = SecurityUser.getUser();

        // Check permissions
        if (!agentService.checkAgentPermission(agentId, user.getId())) {
            return new Result<String>().error("No permission to view the MCP access point address of this agent");
        }
        String agentMcpAccessAddress = agentMcpAccessPointService.getAgentMcpAccessAddress(agentId);
        if (agentMcpAccessAddress == null) {
            return new Result<String>().ok("Please contact the administrator to configure the MCP access point address in parameter management");
        }
        return new Result<String>().ok(agentMcpAccessAddress);
    }

    @Operation(summary = "Get agent MCP tools list")
    @GetMapping("/tools/{agentId}")
    @RequiresPermissions("sys:role:normal")
    public Result<List<String>> getAgentMcpToolsList(@PathVariable("agentId") String agentId) {
        // Get current user
        UserDetail user = SecurityUser.getUser();

        // Check permissions
        if (!agentService.checkAgentPermission(agentId, user.getId())) {
            return new Result<List<String>>().error("No permission to view the MCP tools list of this agent");
        }
        List<String> agentMcpToolsList = agentMcpAccessPointService.getAgentMcpToolsList(agentId);
        return new Result<List<String>>().ok(agentMcpToolsList);
    }
}
