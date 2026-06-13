package xiaozhi.modules.sys.service;


import java.util.function.Consumer;

/**
 * Define a system user utility class to avoid circular dependency with user module
 * For example, user and device depend on each other, user needs to get all devices, device needs to get username for each device
 * @author zjy
 * @since 2025-4-2
 */
public interface SysUserUtilService {
    /**
     * Assign username
     * @param userId User id
     * @param setter Setter method
     */
    void assignUsername( Long userId, Consumer<String> setter);
}
