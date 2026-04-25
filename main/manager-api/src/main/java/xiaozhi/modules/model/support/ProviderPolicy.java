package xiaozhi.modules.model.support;

import java.util.Locale;
import java.util.Set;

import cn.hutool.json.JSONObject;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.model.entity.ModelProviderEntity;

public final class ProviderPolicy {
    private static final Set<String> DISALLOWED_TOKENS = Set.of(
            "aliyun",
            "bailian",
            "dashscope",
            "qwen",
            "xunfei",
            "iflytek",
            "doubao",
            "volc",
            "huoshan",
            "tencent",
            "coze",
            "baidu",
            "wenxin",
            "qianfan",
            "spark",
            "minimax",
            "moonshot",
            "zhipu",
            "baichuan",
            "deepseek",
            "funasr"
    );

    private ProviderPolicy() {
    }

    public static boolean isAllowedProvider(ModelProviderEntity provider) {
        if (provider == null) {
            return false;
        }
        if (containsDisallowedToken(provider.getProviderCode())) {
            return false;
        }
        if (containsDisallowedToken(provider.getName())) {
            return false;
        }
        if (containsDisallowedToken(provider.getId())) {
            return false;
        }
        return true;
    }

    public static boolean isAllowedModelConfig(ModelConfigEntity config) {
        if (config == null) {
            return false;
        }
        if (containsDisallowedToken(config.getModelCode())) {
            return false;
        }
        if (containsDisallowedToken(config.getModelName())) {
            return false;
        }
        if (containsDisallowedToken(config.getId())) {
            return false;
        }
        if (containsDisallowedToken(config.getDocLink())) {
            return false;
        }
        JSONObject configJson = config.getConfigJson();
        if (configJson != null) {
            String type = configJson.getStr("type");
            if (containsDisallowedToken(type)) {
                return false;
            }
            String baseUrl = configJson.getStr("base_url");
            if (containsDisallowedToken(baseUrl)) {
                return false;
            }
        }
        return true;
    }

    public static boolean isAllowedProviderCode(String providerCode) {
        return !containsDisallowedToken(providerCode);
    }

    private static boolean containsDisallowedToken(String value) {
        if (value == null || value.isBlank()) {
            return false;
        }
        String normalized = value.toLowerCase(Locale.ROOT);
        for (String token : DISALLOWED_TOKENS) {
            if (normalized.contains(token)) {
                return true;
            }
        }
        return false;
    }
}
