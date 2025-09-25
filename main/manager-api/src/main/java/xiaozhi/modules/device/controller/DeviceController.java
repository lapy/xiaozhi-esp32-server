package xiaozhi.modules.device.controller;

import java.util.List;

import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springframework.beans.BeanUtils;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.device.dto.DeviceManualAddDTO;
import xiaozhi.modules.device.dto.DeviceRegisterDTO;
import xiaozhi.modules.device.dto.DeviceUnBindDTO;
import xiaozhi.modules.device.dto.DeviceUpdateDTO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.security.user.SecurityUser;
import xiaozhi.modules.sys.service.SysParamsService;

@Tag(name = "Device Management")
@RestController
@RequestMapping("/device")
public class DeviceController {
    private final DeviceService deviceService;
    private final RedisUtils redisUtils;
    private final SysParamsService sysParamsService;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public DeviceController(DeviceService deviceService, RedisUtils redisUtils, SysParamsService sysParamsService,
            RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.deviceService = deviceService;
        this.redisUtils = redisUtils;
        this.sysParamsService = sysParamsService;
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @PostMapping("/bind/{agentId}/{deviceCode}")
    @Operation(summary = "Bind Device")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> bindDevice(@PathVariable String agentId, @PathVariable String deviceCode) {
        deviceService.deviceActivation(agentId, deviceCode);
        return new Result<>();
    }

    @PostMapping("/register")
    @Operation(summary = "Register Device")
    public Result<String> registerDevice(@RequestBody DeviceRegisterDTO deviceRegisterDTO) {
        String macAddress = deviceRegisterDTO.getMacAddress();
        if (StringUtils.isBlank(macAddress)) {
            return new Result<String>().error(ErrorCode.NOT_NULL, "MAC address cannot be empty");
        }
        // Generate six-digit verification code
        String code = String.valueOf(Math.random()).substring(2, 8);
        String key = RedisKeys.getDeviceCaptchaKey(code);
        String existsMac = null;
        do {
            existsMac = (String) redisUtils.get(key);
        } while (StringUtils.isNotBlank(existsMac));

        redisUtils.set(key, macAddress);
        return new Result<String>().ok(code);
    }

    @GetMapping("/bind/{agentId}")
    @Operation(summary = "Get Bound Devices")
    @RequiresPermissions("sys:role:normal")
    public Result<List<DeviceEntity>> getUserDevices(@PathVariable String agentId) {
        UserDetail user = SecurityUser.getUser();
        List<DeviceEntity> devices = deviceService.getUserDevices(user.getId(), agentId);
        return new Result<List<DeviceEntity>>().ok(devices);
    }

    @PostMapping("/bind/{agentId}")
    @Operation(summary = "Forward POST Request to MQTT Gateway")
    @RequiresPermissions("sys:role:normal")
    public Result<String> forwardToMqttGateway(@PathVariable String agentId, @RequestBody String requestBody) {
        try {
            // Get MQTT gateway address from system parameters
            String mqttGatewayUrl = sysParamsService.getValue("server.mqtt_manager_api", true);
            if (StringUtils.isBlank(mqttGatewayUrl) || "null".equals(mqttGatewayUrl)) {
                return new Result<>();
            }

            // Get current user's device list
            UserDetail user = SecurityUser.getUser();
            List<DeviceEntity> devices = deviceService.getUserDevices(user.getId(), agentId);

            // Build deviceIds array
            java.util.List<String> deviceIds = new java.util.ArrayList<>();
            for (DeviceEntity device : devices) {
                String macAddress = device.getMacAddress() != null ? device.getMacAddress() : "unknown";
                String groupId = device.getBoard() != null ? device.getBoard() : "GID_default";

                // Replace colons with underscores
                groupId = groupId.replace(":", "_");
                macAddress = macAddress.replace(":", "_");

                // Build MQTT client ID format: groupId@@@macAddress@@@macAddress
                String mqttClientId = groupId + "@@@" + macAddress + "@@@" + macAddress;
                deviceIds.add(mqttClientId);
            }

            // Build complete URL
            String url = "http://" + mqttGatewayUrl + "/api/devices/status";

            // Set request headers
            HttpHeaders headers = new HttpHeaders();
            headers.set("Content-Type", "application/json");

            // Generate Bearer token
            String token = generateBearerToken();
            if (token == null) {
                return new Result<String>().error("Token generation failed");
            }
            headers.set("Authorization", "Bearer " + token);

            // Build request body JSON
            String jsonBody = "{\"clientIds\":" + objectMapper.writeValueAsString(deviceIds) + "}";
            HttpEntity<String> requestEntity = new HttpEntity<>(jsonBody, headers);

            // Send POST request
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, requestEntity, String.class);

            // Return response
            return new Result<String>().ok(response.getBody());
        } catch (Exception e) {
            return new Result<String>().error("Forward request failed: " + e.getMessage());
        }
    }

    private String generateBearerToken() {
        try {
            // Get current date in yyyy-MM-dd format
            String dateStr = java.time.LocalDate.now()
                    .format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd"));

            // Get MQTT signature key
            String signatureKey = sysParamsService.getValue("server.mqtt_signature_key", false);
            if (StringUtils.isBlank(signatureKey)) {
                return null;
            }

            // Concatenate date string with MQTT_SIGNATURE_KEY
            String tokenContent = dateStr + signatureKey;

            // Perform SHA256 hash calculation on the concatenated string
            String token = org.apache.commons.codec.digest.DigestUtils.sha256Hex(tokenContent);

            return token;
        } catch (Exception e) {
            return null;
        }
    }

    @PostMapping("/unbind")
    @Operation(summary = "Unbind Device")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> unbindDevice(@RequestBody DeviceUnBindDTO unDeviveBind) {
        UserDetail user = SecurityUser.getUser();
        deviceService.unbindDevice(user.getId(), unDeviveBind.getDeviceId());
        return new Result<Void>();
    }

    @PutMapping("/update/{id}")
    @Operation(summary = "Update Device Information")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> updateDeviceInfo(@PathVariable String id, @Valid @RequestBody DeviceUpdateDTO deviceUpdateDTO) {
        DeviceEntity entity = deviceService.selectById(id);
        if (entity == null) {
            return new Result<Void>().error("Device does not exist");
        }
        UserDetail user = SecurityUser.getUser();
        if (!entity.getUserId().equals(user.getId())) {
            return new Result<Void>().error("Device does not exist");
        }
        BeanUtils.copyProperties(deviceUpdateDTO, entity);
        deviceService.updateById(entity);
        return new Result<Void>();
    }

    @PostMapping("/manual-add")
    @Operation(summary = "Manually Add Device")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> manualAddDevice(@RequestBody @Valid DeviceManualAddDTO dto) {
        UserDetail user = SecurityUser.getUser();
        deviceService.manualAddDevice(user.getId(), dto);
        return new Result<>();
    }

    @PostMapping("/commands/{deviceId}")
    @Operation(summary = "Send Device Command")
    @RequiresPermissions("sys:role:normal")
    public Result<String> sendDeviceCommand(@PathVariable String deviceId, @RequestBody String command) {
        try {
            // Get MQTT gateway address from system parameters
            String mqttGatewayUrl = sysParamsService.getValue("server.mqtt_manager_api", true);
            if (StringUtils.isBlank(mqttGatewayUrl) || "null".equals(mqttGatewayUrl)) {
                return new Result<String>().error("MQTT gateway address not configured");
            }

            // Build complete URL
            // Get device information to build mqttClientId
            DeviceEntity deviceById = deviceService.selectById(deviceId);

            if (!deviceById.getUserId().equals(SecurityUser.getUser().getId())) {
                return new Result<String>().error("Device does not exist");
            }
            String macAddress = deviceById != null ? deviceById.getMacAddress() : "unknown";
            String groupId = deviceById != null ? deviceById.getBoard() : null;
            if (groupId == null) {
                groupId = "GID_default";
            }
            groupId = groupId.replace(":", "_");
            macAddress = macAddress.replace(":", "_");

            // Concatenate to groupId@@@macAddress@@@deviceId format
            String mqttClientId = groupId + "@@@" + macAddress + "@@@" + macAddress;

            String url = "http://" + mqttGatewayUrl + "/api/commands/" + mqttClientId;

            // Set request headers
            HttpHeaders headers = new HttpHeaders();
            headers.set("Content-Type", "application/json");

            // Generate Bearer token
            String dateStr = java.time.LocalDate.now()
                    .format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            String signatureKey = sysParamsService.getValue("server.mqtt_signature_key", false);
            if (StringUtils.isBlank(signatureKey)) {
                return new Result<String>().error("MQTT signature key not configured");
            }
            String tokenContent = dateStr + signatureKey;
            String token = org.apache.commons.codec.digest.DigestUtils.sha256Hex(tokenContent);
            headers.set("Authorization", "Bearer " + token);

            // Build request body
            HttpEntity<String> requestEntity = new HttpEntity<>(command, headers);

            // Send POST request
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, requestEntity, String.class);

            // Return response
            return new Result<String>().ok(response.getBody());
        } catch (Exception e) {
            return new Result<String>().error("Failed to send command: " + e.getMessage());
        }
    }
}