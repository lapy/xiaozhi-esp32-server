package xiaozhi.modules.agent.Enums;

import xiaozhi.common.utils.JsonUtils;
import xiaozhi.common.utils.JsonRpcTwo;

import java.util.Map;


/**
 * XiaoZhi MCP JSON-RPC request json
 */
public class XiaoZhiMcpJsonRpcJson {
    //XiaoZhi initialize MCP request json
    private static final String INITIALIZE_JSON;
    //XiaoZhi MCP initialization successful, return notification request json
    private static final String NOTIFICATIONS_INITIALIZED_JSON;
    //XiaoZhi MCP get MCP tool collection request json
    private static final String TOOLS_LIST_REQUEST;
    // Lazy loading
    static {
        INITIALIZE_JSON = JsonUtils.toJsonString(new JsonRpcTwo("initialize",
                Map.of(
                        "protocolVersion", "2024-11-05",
                        "capabilities", Map.of(
                                "roots", Map.of("listChanged", false),
                                "sampling", Map.of()),
                        "clientInfo", Map.of(
                                "name", "xz-mcp-broker",
                                "version", "0.0.1")),
                1));
        NOTIFICATIONS_INITIALIZED_JSON = "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}";
        TOOLS_LIST_REQUEST = JsonUtils.toJsonString(new JsonRpcTwo("tools/list", null, 2));
    }
    public static String getInitializeJson(){
        return INITIALIZE_JSON;
    }
    public static String getNotificationsInitializedJson(){
        return NOTIFICATIONS_INITIALIZED_JSON;
    }
    public static String getToolsListJson(){
        return TOOLS_LIST_REQUEST;
    }

}
