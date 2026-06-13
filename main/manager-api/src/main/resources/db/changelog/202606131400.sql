-- Fix addressBook placed at JSON root by 202605251426.sql and enable westernized web menu defaults.
UPDATE sys_params
SET param_value = CAST(
    JSON_REMOVE(
        JSON_SET(
            CAST(param_value AS JSON),
            '$.features.addressBook',
            JSON_EXTRACT(CAST(param_value AS JSON), '$.addressBook')
        ),
        '$.addressBook'
    ) AS CHAR
)
WHERE param_code = 'system-web.menu'
  AND JSON_CONTAINS_PATH(CAST(param_value AS JSON), 'one', '$.addressBook')
  AND NOT JSON_CONTAINS_PATH(CAST(param_value AS JSON), 'one', '$.features.addressBook');

UPDATE sys_params
SET param_value = CAST(
    JSON_SET(
        CAST(param_value AS JSON),
        '$.features.addressBook',
        JSON_OBJECT(
            'name', 'feature.addressBook.name',
            'enabled', TRUE,
            'description', 'feature.addressBook.description'
        )
    ) AS CHAR
)
WHERE param_code = 'system-web.menu'
  AND NOT JSON_CONTAINS_PATH(CAST(param_value AS JSON), 'one', '$.features.addressBook');

UPDATE sys_params
SET param_value = CAST(
    JSON_SET(
        CAST(param_value AS JSON),
        '$.features.voiceClone.enabled', TRUE,
        '$.features.knowledgeBase.enabled', TRUE,
        '$.features.addressBook.enabled', TRUE,
        '$.groups.featureManagement',
        JSON_ARRAY('voiceprintRecognition', 'voiceClone', 'knowledgeBase', 'mcpAccessPoint', 'addressBook')
    ) AS CHAR
)
WHERE param_code = 'system-web.menu';
