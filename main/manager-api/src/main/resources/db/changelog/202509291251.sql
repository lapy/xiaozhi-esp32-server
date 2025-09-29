--
-- Update exit commands configuration to include bye and goodbye
-- Migration date: 2025-09-29 12:51
-- Author: ai_assistant
--

-- Update exit commands configuration to include bye and goodbye
UPDATE `sys_params` 
SET `param_value` = 'exit;close;bye;goodbye',
    `update_date` = '2025-09-29 12:51:00'
WHERE `param_code` = 'exit_commands';

-- Update wakeup words configuration with new comprehensive list
UPDATE `sys_params` 
SET `param_value` = 'Alexa;Hi ESP;Jarvis;computer;Hey Willow;Sophia;Hey Wanda;Hi Jolly;Hi Fairy;Hey Printer;Mycroft;Hi Joy;Hi Jason;Astrolabe;Hey Ily;Blue Chip;Hi Lily;Hi Telly;Hi Wall E',
    `update_date` = '2025-09-29 12:51:00'
WHERE `param_code` = 'wakeup_words';
