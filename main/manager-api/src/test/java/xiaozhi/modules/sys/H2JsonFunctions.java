package xiaozhi.modules.sys;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;

public final class H2JsonFunctions {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private H2JsonFunctions() {
    }

    public static String jsonSet(String json, String path1, String value1) throws IOException {
        ObjectNode root = asObjectNode(json);
        setJsonPath(root, path1, value1);
        return OBJECT_MAPPER.writeValueAsString(root);
    }

    public static String jsonSet(String json, String path1, String value1, String path2, String value2) throws IOException {
        ObjectNode root = asObjectNode(json);
        setJsonPath(root, path1, value1);
        setJsonPath(root, path2, value2);
        return OBJECT_MAPPER.writeValueAsString(root);
    }

    public static String jsonSet(
        String json,
        String path1,
        String value1,
        String path2,
        String value2,
        String path3,
        String value3
    ) throws IOException {
        ObjectNode root = asObjectNode(json);
        setJsonPath(root, path1, value1);
        setJsonPath(root, path2, value2);
        setJsonPath(root, path3, value3);
        return OBJECT_MAPPER.writeValueAsString(root);
    }

    public static String jsonRemove(String json, String path) throws IOException {
        ObjectNode root = asObjectNode(json);
        String[] tokens = tokenizePath(path);
        ObjectNode current = root;
        for (int i = 0; i < tokens.length - 1; i++) {
            JsonNode next = current.get(tokens[i]);
            if (!(next instanceof ObjectNode)) {
                return OBJECT_MAPPER.writeValueAsString(root);
            }
            current = (ObjectNode) next;
        }
        current.remove(tokens[tokens.length - 1]);
        return OBJECT_MAPPER.writeValueAsString(root);
    }

    public static String jsonRemove(String json, String path1, String path2) throws IOException {
        return jsonRemove(jsonRemove(json, path1), path2);
    }

    public static String jsonRemove(String json, String path1, String path2, String path3) throws IOException {
        return jsonRemove(jsonRemove(json, path1, path2), path3);
    }

    public static String jsonRemove(String json, String path1, String path2, String path3, String path4) throws IOException {
        return jsonRemove(jsonRemove(json, path1, path2, path3), path4);
    }

    public static String jsonRemove(
        String json,
        String path1,
        String path2,
        String path3,
        String path4,
        String path5
    ) throws IOException {
        return jsonRemove(jsonRemove(json, path1, path2, path3, path4), path5);
    }

    public static String jsonExtract(String json, String path) throws IOException {
        if (json == null || json.isBlank()) {
            return null;
        }
        JsonNode current = OBJECT_MAPPER.readTree(json);
        for (String token : tokenizePath(path)) {
            if (current == null) {
                return null;
            }
            current = current.get(token);
        }
        if (current == null || current.isNull()) {
            return null;
        }
        if (current.isTextual()) {
            return current.textValue();
        }
        if (current.isNumber() || current.isBoolean()) {
            return current.asText();
        }
        return OBJECT_MAPPER.writeValueAsString(current);
    }

    public static String jsonUnquote(String value) {
        if (value == null) {
            return null;
        }
        if (value.length() >= 2 && value.startsWith("\"") && value.endsWith("\"")) {
            return value.substring(1, value.length() - 1);
        }
        return value;
    }

    public static String filterProviderFields(String json, String keyToRemove) throws IOException {
        if (json == null || json.isBlank()) {
            return json;
        }
        JsonNode node = OBJECT_MAPPER.readTree(json);
        if (!(node instanceof ArrayNode arrayNode)) {
            return json;
        }

        ArrayNode filtered = OBJECT_MAPPER.createArrayNode();
        for (JsonNode item : arrayNode) {
            if (!item.isObject()) {
                filtered.add(item);
                continue;
            }
            String key = item.path("key").asText();
            if (!keyToRemove.equals(key)) {
                filtered.add(item);
            }
        }
        return OBJECT_MAPPER.writeValueAsString(filtered);
    }

    private static ObjectNode asObjectNode(String json) throws IOException {
        if (json == null || json.isBlank()) {
            return OBJECT_MAPPER.createObjectNode();
        }
        JsonNode node = OBJECT_MAPPER.readTree(json);
        if (node instanceof ObjectNode objectNode) {
            return objectNode;
        }
        return OBJECT_MAPPER.createObjectNode();
    }

    private static void setJsonPath(ObjectNode root, String path, String value) throws IOException {
        String[] tokens = tokenizePath(path);
        ObjectNode current = root;
        for (int i = 0; i < tokens.length - 1; i++) {
            JsonNode next = current.get(tokens[i]);
            if (!(next instanceof ObjectNode)) {
                next = OBJECT_MAPPER.createObjectNode();
                current.set(tokens[i], next);
            }
            current = (ObjectNode) next;
        }
        current.set(tokens[tokens.length - 1], coerceJsonValue(value));
    }

    private static String[] tokenizePath(String path) {
        return path.replaceFirst("^\\$\\.", "").split("\\.");
    }

    private static JsonNode coerceJsonValue(String value) throws IOException {
        if (value == null) {
            return OBJECT_MAPPER.nullNode();
        }
        String trimmed = value.trim();
        if ((trimmed.startsWith("{") && trimmed.endsWith("}")) || (trimmed.startsWith("[") && trimmed.endsWith("]"))) {
            return OBJECT_MAPPER.readTree(trimmed);
        }
        if ("null".equalsIgnoreCase(trimmed)) {
            return OBJECT_MAPPER.nullNode();
        }
        if ("true".equalsIgnoreCase(trimmed) || "false".equalsIgnoreCase(trimmed)) {
            return OBJECT_MAPPER.valueToTree(Boolean.parseBoolean(trimmed));
        }
        if (trimmed.matches("-?\\d+")) {
            try {
                return OBJECT_MAPPER.valueToTree(Integer.parseInt(trimmed));
            } catch (NumberFormatException ignored) {
                return OBJECT_MAPPER.valueToTree(Long.parseLong(trimmed));
            }
        }
        if (trimmed.matches("-?\\d+\\.\\d+")) {
            return OBJECT_MAPPER.valueToTree(Double.parseDouble(trimmed));
        }
        return OBJECT_MAPPER.valueToTree(value);
    }
}
