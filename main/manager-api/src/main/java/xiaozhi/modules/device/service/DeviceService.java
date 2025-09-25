package xiaozhi.modules.device.service;

import java.util.Date;
import java.util.List;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.device.dto.DevicePageUserDTO;
import xiaozhi.modules.device.dto.DeviceReportReqDTO;
import xiaozhi.modules.device.dto.DeviceReportRespDTO;
import xiaozhi.modules.device.dto.DeviceManualAddDTO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.vo.UserShowDeviceListVO;

public interface DeviceService extends BaseService<DeviceEntity> {

    /**
     * Check if device is activated
     */
    DeviceReportRespDTO checkDeviceActive(String macAddress, String clientId,
            DeviceReportReqDTO deviceReport);

    /**
     * Get device list for user specified agent,
     */
    List<DeviceEntity> getUserDevices(Long userId, String agentId);

    /**
     * Unbind device
     */
    void unbindDevice(Long userId, String deviceId);

    /**
     * Device activation
     */
    Boolean deviceActivation(String agentId, String activationCode);

    /**
     * Delete all devices for this user
     * 
     * @param userId User ID
     */
    void deleteByUserId(Long userId);

    /**
     * Delete all devices associated with the specified agent
     * 
     * @param agentId Agent ID
     */
    void deleteByAgentId(String agentId);

    /**
     * Get device count for specified user
     * 
     * @param userId User ID
     * @return Device count
     */
    Long selectCountByUserId(Long userId);

    /**
     * Get all device information with pagination
     *
     * @param dto Pagination search parameters
     * @return User list pagination data
     */
    PageData<UserShowDeviceListVO> page(DevicePageUserDTO dto);

    /**
     * Get device information by MAC address
     * 
     * @param macAddress MAC address
     * @return Device information
     */
    DeviceEntity getDeviceByMacAddress(String macAddress);

    /**
     * Get activation code by device ID
     * 
     * @param deviceId Device ID
     * @return Activation code
     */
    String geCodeByDeviceId(String deviceId);

    /**
     * Get the latest last connection time for this agent device
     * @param agentId Agent ID
     * @return Device latest last connection time
     */
    Date getLatestLastConnectionTime(String agentId);

    /**
     * Manually add device
     */
    void manualAddDevice(Long userId, DeviceManualAddDTO dto);

    /**
     * Update device connection information
     */
    void updateDeviceConnectionInfo(String agentId, String deviceId, String appVersion);

}