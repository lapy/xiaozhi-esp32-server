package xiaozhi.modules.config.init;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

import jakarta.annotation.PostConstruct;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.modules.config.service.ConfigService;
import xiaozhi.modules.sys.service.SysParamsService;

@Configuration
public class SystemInitConfig {

    @Autowired
    private SysParamsService sysParamsService;

    @Autowired
    private ConfigService configService;

    @Autowired
    private RedisUtils redisUtils;

    @Autowired
    private Environment environment;

    @PostConstruct
    public void init() {
        // Skip Redis operations during testing
        if (environment.acceptsProfiles("test")) {
            return;
        }

        // Check version number
        String redisVersion = (String) redisUtils.get(RedisKeys.getVersionKey());
        if (!Constant.VERSION.equals(redisVersion)) {
            // If version is inconsistent, clear Redis
            redisUtils.emptyAll();
            // Store new version number
            redisUtils.set(RedisKeys.getVersionKey(), Constant.VERSION);
        }

        sysParamsService.initServerSecret();
        configService.getConfig(false);
    }
}