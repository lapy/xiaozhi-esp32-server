package xiaozhi.modules.sys.service;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.sys.dto.AdminPageUserDTO;
import xiaozhi.modules.sys.dto.PasswordDTO;
import xiaozhi.modules.sys.dto.SysUserDTO;
import xiaozhi.modules.sys.entity.SysUserEntity;
import xiaozhi.modules.sys.vo.AdminPageUserVO;

/**
 * System User
 */
public interface SysUserService extends BaseService<SysUserEntity> {

    SysUserDTO getByUsername(String username);

    SysUserDTO getByUserId(Long userId);

    void save(SysUserDTO dto);

    /**
     * Delete specified user and associated data devices and agents
     * 
     * @param ids
     */
    void deleteById(Long ids);

    /**
     * Verify if password change is allowed
     * 
     * @param userId      User ID
     * @param passwordDTO Password verification parameters
     */
    void changePassword(Long userId, PasswordDTO passwordDTO);

    /**
     * Directly modify password without verification
     * 
     * @param userId   User ID
     * @param password Password
     */
    void changePasswordDirectly(Long userId, String password);

    /**
     * Reset password
     * 
     * @param userId User ID
     * @return Randomly generated password that meets specifications
     */
    String resetPassword(Long userId);

    /**
     * Administrator paginated user information
     * 
     * @param dto Pagination search parameters
     * @return User list pagination data
     */
    PageData<AdminPageUserVO> page(AdminPageUserDTO dto);

    /**
     * Batch modify user status
     * 
     * @param status  User status
     * @param userIds User ID array
     */
    void changeStatus(Integer status, String[] userIds);

    /**
     * Get whether user registration is allowed
     * 
     * @return Whether user registration is allowed
     */
    boolean getAllowUserRegister();
}
