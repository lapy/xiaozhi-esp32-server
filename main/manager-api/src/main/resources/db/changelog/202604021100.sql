-- Relabel the downstream tool-call timeout seed so no Han-script remains
-- in sys_params after the full westernization cleanup queue has run.
UPDATE `sys_params`
SET `remark` = 'Tool call timeout in seconds'
WHERE `param_code` = 'tool_call_timeout';
