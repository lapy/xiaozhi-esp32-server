package xiaozhi.modules.agent.service;


import java.util.List;

/**
 * Agent MCP access point processing service
 *
 * @author zjy
 */
public interface AgentMcpAccessPointService {
    /**
     * Get agent MCP access point address
     * @param id Agent id
     * @return MCP access point address
     */
   String getAgentMcpAccessAddress(String id);

    /**
     * Get the existing tool list for the agent's MCP access point
     * @param id Agent id
     * @return Tool list
     */
   List<String> getAgentMcpToolsList(String id);
}
