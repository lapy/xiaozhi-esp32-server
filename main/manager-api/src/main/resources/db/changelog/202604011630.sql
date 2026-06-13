-- Relocalize the remaining sys_params remarks that still leak Chinese
-- into downstream admin defaults after the broader seed cleanup.

UPDATE `sys_params` SET `remark` = 'Disconnect after this many seconds without voice input' WHERE `param_code` = 'close_connection_no_voice_time';
UPDATE `sys_params` SET `remark` = 'Delete generated audio files after use' WHERE `param_code` = 'delete_audio';
UPDATE `sys_params` SET `remark` = 'Maximum output characters per device per day; 0 disables the limit' WHERE `param_code` = 'device_max_output_size';
UPDATE `sys_params` SET `remark` = 'Enable greeting replies' WHERE `param_code` = 'enable_greeting';
UPDATE `sys_params` SET `remark` = 'Enable wakeword response acceleration' WHERE `param_code` = 'enable_wakeup_words_response_cache';
UPDATE `sys_params` SET `remark` = 'Enable WebSocket heartbeat keepalive' WHERE `param_code` = 'enable_websocket_ping';
UPDATE `sys_params` SET `remark` = 'Enable end prompt' WHERE `param_code` = 'end_prompt.enable';
UPDATE `sys_params` SET `remark` = 'Data directory' WHERE `param_code` = 'log.data_dir';
UPDATE `sys_params` SET `remark` = 'Log directory' WHERE `param_code` = 'log.log_dir';
UPDATE `sys_params` SET `remark` = 'Log filename' WHERE `param_code` = 'log.log_file';
UPDATE `sys_params` SET `remark` = 'Console log format' WHERE `param_code` = 'log.log_format';
UPDATE `sys_params` SET `remark` = 'File log format' WHERE `param_code` = 'log.log_format_file';
UPDATE `sys_params` SET `remark` = 'Log level' WHERE `param_code` = 'log.log_level';
UPDATE `sys_params` SET `remark` = 'Allow registration for non-admin users' WHERE `param_code` = 'server.allow_user_register';
UPDATE `sys_params` SET `remark` = 'Enable token authentication for the server module' WHERE `param_code` = 'server.auth.enabled';
UPDATE `sys_params` SET `remark` = 'Control panel URL displayed with the six-digit binding code' WHERE `param_code` = 'server.fronted_url';
UPDATE `sys_params` SET `remark` = 'MCP endpoint address' WHERE `param_code` = 'server.mcp_endpoint';
UPDATE `sys_params` SET `remark` = 'MQTT gateway configuration' WHERE `param_code` = 'server.mqtt_gateway';
UPDATE `sys_params` SET `remark` = 'MQTT gateway management API address' WHERE `param_code` = 'server.mqtt_manager_api';
UPDATE `sys_params` SET `remark` = 'MQTT signature key configuration' WHERE `param_code` = 'server.mqtt_signature_key';
UPDATE `sys_params` SET `remark` = 'OTA service address' WHERE `param_code` = 'server.ota';
UPDATE `sys_params` SET `remark` = 'Server SM2 private key' WHERE `param_code` = 'server.private_key';
UPDATE `sys_params` SET `remark` = 'Server SM2 public key' WHERE `param_code` = 'server.public_key';
UPDATE `sys_params` SET `remark` = 'Server secret' WHERE `param_code` = 'server.secret';
UPDATE `sys_params` SET `remark` = 'UDP gateway configuration' WHERE `param_code` = 'server.udp_gateway';
UPDATE `sys_params` SET `remark` = 'Voiceprint service address' WHERE `param_code` = 'server.voice_print';
UPDATE `sys_params` SET `remark` = 'Voiceprint similarity threshold from 0.0 to 1.0; higher is stricter' WHERE `param_code` = 'server.voiceprint_similarity_threshold';
UPDATE `sys_params` SET `remark` = 'WebSocket address list separated by semicolons' WHERE `param_code` = 'server.websocket';
UPDATE `sys_params` SET `remark` = 'System feature menu configuration' WHERE `param_code` = 'system-web.menu';
UPDATE `sys_params` SET `remark` = 'TTS request timeout in seconds' WHERE `param_code` = 'tts_timeout';
UPDATE `sys_params` SET `remark` = 'Wakeword list used for wakeword recognition' WHERE `param_code` = 'wakeup_words';
