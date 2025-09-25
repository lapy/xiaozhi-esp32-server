--
-- Add SYSTEM_PLUGIN_HA_GET_CALENDAR and SYSTEM_PLUGIN_CHANGE_ROLE to ai_model_provider table
-- Migration date: 2025-09-29 11:42
-- Author: ai_assistant
--

-- Add get_calendar plugin provider to ai_model_provider table
INSERT INTO `ai_model_provider` VALUES (
'SYSTEM_PLUGIN_HA_GET_CALENDAR',
'Plugin',
'get_calendar',
'Standard Calendar Information Service',
'[]',
40,
0,
'2025-09-29 11:42:00',
0,
'2025-09-29 11:42:00'
);

-- Add change_role plugin provider to ai_model_provider table
INSERT INTO `ai_model_provider` VALUES (
'SYSTEM_PLUGIN_CHANGE_ROLE',
'Plugin',
'change_role',
'Role Switching Service',
'[{"key": "available_roles", "type": "string", "label": "Available Roles", "default": "sassy_girlfriend,english_teacher,curious_kid", "description": "Comma-separated list of available roles for switching"}]',
30,
0,
'2025-09-29 11:42:00',
0,
'2025-09-29 11:42:00'
);
