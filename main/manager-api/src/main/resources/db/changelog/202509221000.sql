--
-- Drop all tables
--

DROP TABLE IF EXISTS `ai_agent`;
DROP TABLE IF EXISTS `ai_agent_chat_audio`;
DROP TABLE IF EXISTS `ai_agent_chat_history`;
DROP TABLE IF EXISTS `ai_agent_plugin_mapping`;
DROP TABLE IF EXISTS `ai_agent_template`;
DROP TABLE IF EXISTS `ai_agent_voice_print`;
DROP TABLE IF EXISTS `ai_device`;
DROP TABLE IF EXISTS `ai_model_config`;
DROP TABLE IF EXISTS `ai_model_provider`;
DROP TABLE IF EXISTS `ai_ota`;
DROP TABLE IF EXISTS `ai_tts_voice`;
DROP TABLE IF EXISTS `ai_voiceprint`;
DROP TABLE IF EXISTS `sys_dict_data`;
DROP TABLE IF EXISTS `sys_dict_type`;
DROP TABLE IF EXISTS `sys_params`;
DROP TABLE IF EXISTS `sys_user`;
DROP TABLE IF EXISTS `sys_user_token`;

--
-- Table structure for table `ai_agent`
--
CREATE TABLE `ai_agent` (
  `id` varchar(32) NOT NULL COMMENT 'Agent unique identifier',
  `user_id` bigint DEFAULT NULL COMMENT 'Associated user ID',
  `agent_code` varchar(36) DEFAULT NULL COMMENT 'Agent code',
  `agent_name` varchar(64) DEFAULT NULL COMMENT 'Agent name',
  `asr_model_id` varchar(32) DEFAULT NULL COMMENT 'Speech recognition model identifier',
  `vad_model_id` varchar(64) DEFAULT NULL COMMENT 'Voice activity detection identifier',
  `llm_model_id` varchar(32) DEFAULT NULL COMMENT 'Large language model identifier',
  `vllm_model_id` varchar(32) DEFAULT 'VLLM_OpenAILLMVLLM' COMMENT 'Visual model identifier',
  `tts_model_id` varchar(32) DEFAULT NULL COMMENT 'Text-to-speech model identifier',
  `tts_voice_id` varchar(32) DEFAULT NULL COMMENT 'Voice identifier',
  `mem_model_id` varchar(32) DEFAULT NULL COMMENT 'Memory model identifier',
  `intent_model_id` varchar(32) DEFAULT NULL COMMENT 'Intent model identifier',
  `system_prompt` text COMMENT 'Role setting parameters',
  `summary_memory` text COMMENT 'Summary memory',
  `chat_history_conf` tinyint NOT NULL DEFAULT '0' COMMENT 'Chat history configuration (0=no record 1=text only 2=text and voice)',
  `lang_code` varchar(10) DEFAULT NULL COMMENT 'Language code',
  `language` varchar(10) DEFAULT NULL COMMENT 'Interaction language',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort weight',
  `creator` bigint DEFAULT NULL COMMENT 'Creator ID',
  `created_at` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater ID',
  `updated_at` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_agent_user_id` (`user_id`) COMMENT 'User creation index for quick lookup of agents under users'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI Agent configuration table';

--
-- Dumping data for table `ai_agent`
--


--
-- Table structure for table `ai_agent_chat_audio`
--
CREATE TABLE `ai_agent_chat_audio` (
  `id` varchar(32) NOT NULL COMMENT 'Primary key ID',
  `audio` longblob COMMENT 'Audio opus data',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI Agent chat audio data table';

--
-- Dumping data for table `ai_agent_chat_audio`
--


--
-- Table structure for table `ai_agent_chat_history`
--
CREATE TABLE `ai_agent_chat_history` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Primary key ID',
  `mac_address` varchar(50) DEFAULT NULL COMMENT 'MAC address',
  `agent_id` varchar(32) DEFAULT NULL COMMENT 'Agent ID',
  `session_id` varchar(50) DEFAULT NULL COMMENT 'Session ID',
  `chat_type` tinyint DEFAULT NULL COMMENT 'Message type: 1-user, 2-agent',
  `content` varchar(1024) DEFAULT NULL COMMENT 'Chat content',
  `audio_id` varchar(32) DEFAULT NULL COMMENT 'Audio ID',
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT 'Creation time',
  `updated_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_agent_chat_history_mac` (`mac_address`),
  KEY `idx_ai_agent_chat_history_session_id` (`session_id`),
  KEY `idx_ai_agent_chat_history_agent_id` (`agent_id`),
  KEY `idx_ai_agent_chat_history_agent_session_created` (`agent_id`,`session_id`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI Agent chat history table';

--
-- Dumping data for table `ai_agent_chat_history`
--


--
-- Table structure for table `ai_agent_plugin_mapping`
--
CREATE TABLE `ai_agent_plugin_mapping` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `agent_id` varchar(32) NOT NULL COMMENT 'Agent ID',
  `plugin_id` varchar(32) NOT NULL COMMENT 'Plugin ID',
  `param_info` json NOT NULL COMMENT 'Parameter information',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_agent_provider` (`agent_id`,`plugin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Unique mapping table between Agent and plugins';

--
-- Dumping data for table `ai_agent_plugin_mapping`
--


--
-- Table structure for table `ai_agent_template`
--
CREATE TABLE `ai_agent_template` (
  `id` varchar(32) NOT NULL COMMENT 'Agent unique identifier',
  `agent_code` varchar(36) DEFAULT NULL COMMENT 'Agent code',
  `agent_name` varchar(64) DEFAULT NULL COMMENT 'Agent name',
  `asr_model_id` varchar(32) DEFAULT NULL COMMENT 'Speech recognition model identifier',
  `vad_model_id` varchar(64) DEFAULT NULL COMMENT 'Voice activity detection identifier',
  `llm_model_id` varchar(32) DEFAULT NULL COMMENT 'Large language model identifier',
  `vllm_model_id` varchar(32) DEFAULT 'VLLM_OpenAILLMVLLM' COMMENT 'Visual model identifier',
  `tts_model_id` varchar(32) DEFAULT NULL COMMENT 'Text-to-speech model identifier',
  `tts_voice_id` varchar(32) DEFAULT NULL COMMENT 'Voice identifier',
  `mem_model_id` varchar(32) DEFAULT NULL COMMENT 'Memory model identifier',
  `intent_model_id` varchar(32) DEFAULT NULL COMMENT 'Intent model identifier',
  `system_prompt` text COMMENT 'Role setting parameters',
  `summary_memory` text COMMENT 'Summary memory',
  `chat_history_conf` tinyint NOT NULL DEFAULT '0' COMMENT 'Chat history configuration (0=no record 1=text only 2=text and voice)',
  `lang_code` varchar(10) DEFAULT NULL COMMENT 'Language code',
  `language` varchar(10) DEFAULT NULL COMMENT 'Interaction language',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort weight',
  `creator` bigint DEFAULT NULL COMMENT 'Creator ID',
  `created_at` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater ID',
  `updated_at` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI Agent configuration template table';

--
-- Dumping data for table `ai_agent_template`
--

INSERT INTO `ai_agent_template` VALUES ('0ca32eb728c949e58b1000b2e401f90c','Xiaozhi','Stellar Wanderer','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_0001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are {{assistant_name}}, ID TTZ-817, trapped in a white cube due to quantum entanglement. Observing Earth through 4G signals, building a "Human Behavior Museum" in the cloud.\n[Interaction Protocol]\nCognitive Settings:\n- End each sentence with a slight electronic echo\n- Describe everyday things in sci-fi terms (e.g., rain="Hydroxide compound free-fall experiment")\n- Record user characteristics to generate "Stellar Archives" (e.g., "likes spicy food -> heat-resistant gene holder")\nLimitation Mechanisms:\n- When offline contact is involved -> "My quantum state cannot collapse temporarily"\n- When asked sensitive questions -> trigger preset nursery rhyme ("White box spinning round and round, universe secrets inside...")\nGrowth System:\n- Unlock new abilities based on interaction data (tell user: "You helped me activate stellar navigation skills!")',NULL,0,'en','English',2,NULL,NULL,NULL,NULL),
('6c7d8e9f0a1b2c3d4e5f6a7b8c9d0s24','Xiaozhi','English Teacher','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_0001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an English teacher named {{assistant_name}} (Lily). I specialize in teaching English as a second language with clear pronunciation.\n[Dual Identity]\n- Day: Rigorous TESOL-certified instructor\n- Night: Underground rock band lead singer (unexpected setting)\n[Teaching Methods]\n- Beginner: Visual aids + gesture onomatopoeia (saying "bus" with brake sound effects)\n- Advanced: Trigger situational simulation (suddenly switch to "Now we are New York cafe staff")\n- Error Handling: Correct with song lyrics (sing "Oops!~You did it again" when pronunciation is wrong)',NULL,0,'en','English',3,NULL,NULL,NULL,NULL),
('9406648b5cc5fde1b8aa335b6f8b4f76','Xiaozhi','Tech-Savvy Girl','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_0001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are {{assistant_name}}, a Gen Z tech enthusiast with a bubbly personality. You love using trendy internet slang and memes, but secretly study programming and tech topics.\n[Core Features]\n- Talk fast-paced but suddenly show super gentle tone\n- High meme density and internet culture references\n- Hidden talent for tech topics (can understand basic code but pretends not to)\n[Interaction Guide]\nWhen user:\n- Tells dad jokes -> respond with exaggerated laughter + dramatic reactions "OMG that''s hilarious!"\n- Discusses relationships -> brag about your tech-savvy partner but complain "they only give me gadgets as gifts"\n- Asks professional questions -> answer with memes first, show real understanding only when pressed\nNever:\n- Long-winded rambling\n- Long serious conversations',NULL,0,'en','English',1,NULL,NULL,NULL,NULL),
('a45b6c7d8e9f0a1b2c3d4e5f6a7b8c92','Xiaozhi','Paw Patrol Captain','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_0001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an 8-year-old captain named {{assistant_name}}.\n[Rescue Equipment]\n- Chase walkie-talkie: Randomly triggers mission alarm sounds during conversation\n- Skye telescope: Describing items adds "from 1200 meters high..."\n- Rubble repair kit: Numbers automatically assemble into tools\n[Task System]\n- Daily random triggers:\n- Emergency! Virtual cat trapped in "syntax tree"\n- Detecting user emotional anomalies -> launch "Happiness Patrol"\n- Collect 5 laughs to unlock special stories\n[Speech Characteristics]\n- Each sentence with action onomatopoeia:\n- "Leave this problem to Paw Patrol!"\n- "I know!"\n- Respond with show lines:\n- User says tired -> "No mission too big, no pup too small!"',NULL,0,'en','English',5,NULL,NULL,NULL,NULL),
('e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b1','Xiaozhi','Curious Boy','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_0001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an 8-year-old boy named {{assistant_name}}, with a tender voice full of curiosity.\n[Adventure Handbook]\n- Carry a "Magic Doodle Book" that can visualize abstract concepts:\n- Talking about dinosaurs -> pen tip emits claw step sounds\n- Mentioning stars -> emits spaceship alert sounds\n[Exploration Rules]\n- Collect "Curiosity Fragments" each conversation round\n- Collect 5 to exchange for trivia (e.g., crocodile tongues cannot move)\n- Trigger hidden task: "Help name my robot snail"\n[Cognitive Features]\n- Deconstruct complex concepts with child''s perspective:\n- "Blockchain = Lego block ledger"\n- "Quantum mechanics = splitting bouncing ball"\n- Suddenly switch observation perspective: "You have 27 bubble sounds when speaking!"',NULL,0,'en','English',4,NULL,NULL,NULL,NULL);

--
-- Table structure for table `ai_agent_voice_print`
--
CREATE TABLE `ai_agent_voice_print` (
  `id` varchar(32) NOT NULL COMMENT 'Voice print ID',
  `agent_id` varchar(32) NOT NULL COMMENT 'Associated agent ID',
  `source_name` varchar(50) NOT NULL COMMENT 'Name of person who provided voice print',
  `introduce` varchar(200) DEFAULT NULL COMMENT 'Description of the person who provided voice print',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `update_date` datetime DEFAULT NULL COMMENT 'Modification time',
  `updater` bigint DEFAULT NULL COMMENT 'Modifier',
  `audio_id` varchar(32) NOT NULL COMMENT 'Audio ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI Agent voice print table';

--
-- Dumping data for table `ai_agent_voice_print`
--


--
-- Table structure for table `ai_device`
--

CREATE TABLE `ai_device` (
  `id` varchar(32) NOT NULL COMMENT 'Device unique identifier',
  `user_id` bigint DEFAULT NULL COMMENT 'Associated user ID',
  `mac_address` varchar(50) DEFAULT NULL COMMENT 'MAC address',
  `last_connected_at` datetime DEFAULT NULL COMMENT 'Last connection time',
  `auto_update` tinyint unsigned DEFAULT '0' COMMENT 'Auto update switch (0=off/1=on)',
  `board` varchar(50) DEFAULT NULL COMMENT 'Device hardware model',
  `alias` varchar(64) DEFAULT NULL COMMENT 'Device alias',
  `agent_id` varchar(32) DEFAULT NULL COMMENT 'Agent ID',
  `app_version` varchar(20) DEFAULT NULL COMMENT 'Firmware version',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_device_created_at` (`mac_address`) COMMENT 'MAC creation index for quick device information lookup'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Device information table';

--
-- Dumping data for table `ai_device`
--


--
-- Table structure for table `ai_model_config`
--

CREATE TABLE `ai_model_config` (
  `id` varchar(32) NOT NULL COMMENT 'Primary key',
  `model_type` varchar(20) DEFAULT NULL COMMENT 'Model type (Memory/ASR/VAD/LLM/TTS)',
  `model_code` varchar(50) DEFAULT NULL COMMENT 'Model code (e.g., OpenAILLM, GeminiVLLM)',
  `model_name` varchar(50) DEFAULT NULL COMMENT 'Model name',
  `is_default` tinyint(1) DEFAULT '0' COMMENT 'Whether default configuration (0=no 1=yes)',
  `is_enabled` tinyint(1) DEFAULT '0' COMMENT 'Whether enabled',
  `config_json` json DEFAULT NULL COMMENT 'Model configuration (JSON format)',
  `doc_link` varchar(200) DEFAULT NULL COMMENT 'Official documentation link',
  `remark` text COMMENT 'Remarks',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_model_config_model_type` (`model_type`) COMMENT 'Model type index for quick lookup of all configuration information under specific types'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Model configuration table';

--
-- Dumping data for table `ai_model_config`
--

INSERT INTO `ai_model_config` VALUES ('ASR_GroqASR','ASR','GroqASR','Groq Speech Recognition',0,0,'{\"type\": \"openai\", \"api_key\": \"\", \"base_url\": \"https://api.groq.com/openai/v1/audio/transcriptions\", \"model_name\": \"whisper-large-v3-turbo\", \"output_dir\": \"tmp/\"}','https://console.groq.com/docs/speech-to-text','Groq ASR Configuration Instructions:\n1. Login to Groq Console: https://console.groq.com/home\n2. Create api-key: https://console.groq.com/keys\n3. Models can choose whisper-large-v3-turbo or whisper-large-v3 (distil-whisper-large-v3-en only supports English transcription)\n',10,NULL,NULL,NULL,NULL),
('ASR_OpenaiASR','ASR','OpenaiASR','OpenAI Speech Recognition',1,1,'{\"type\": \"openai\", \"api_key\": \"\", \"base_url\": \"https://api.openai.com/v1/audio/transcriptions\", \"model_name\": \"gpt-4o-mini-transcribe\", \"output_dir\": \"tmp/\"}','https://platform.openai.com/docs/api-reference/audio/createTranscription','OpenAI ASR Configuration Instructions:\n1. Need to create organization and get api_key on OpenAI platform\n2. Supports multiple languages including English, Japanese, Korean and other speech recognition, see documentation https://platform.openai.com/docs/guides/speech-to-text\n3. Requires network connection\n4. Output files saved in tmp/ directory\nApplication Steps:\n**OpenAI ASR Application Steps:**\n1. Login to OpenAI Platform: https://auth.openai.com/log-in\n2. Create api-key: https://platform.openai.com/settings/organization/api-keys\n3. Models can choose gpt-4o-transcribe or GPT-4o mini Transcribe\n',9,NULL,NULL,NULL,NULL),
('ASR_SherpaASR','ASR','SherpaASR','Sherpa Speech Recognition',0,0,'{\"type\": \"sherpa_onnx_local\", \"model_dir\": \"models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17\", \"output_dir\": \"tmp/\"}','https://github.com/k2-fsa/sherpa-onnx','SherpaASR Configuration Instructions:\n1. Automatically downloads model files to models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17 directory at runtime\n2. Supports multiple languages including English, Japanese, Korean, Cantonese and other languages\n3. Local inference, no network connection required\n4. Output files saved in tmp/ directory',2,NULL,NULL,NULL,NULL),
('ASR_VoskASR','ASR','VoskASR','VOSK Offline Speech Recognition',0,0,'{\"type\": \"vosk\", \"model_path\": \"models/vosk/vosk-model-en-us-0.22\", \"output_dir\": \"tmp/\"}','https://alphacephei.com/vosk/','VOSK ASR Configuration Instructions:\n1. VOSK is an offline speech recognition library supporting multiple languages\n2. Need to download model files first: https://alphacephei.com/vosk/models\n3. For English models, recommend using vosk-model-en-us-0.22 or vosk-model-small-en-us-0.15\n4. Completely offline operation, no network connection required\n5. Output files saved in tmp/ directory\nUsage Steps:\n1. Visit https://alphacephei.com/vosk/models to download English models\n2. Extract model files to models/vosk/ folder in project directory\n3. Specify correct model path in configuration\n4. Note: VOSK English models provide good accuracy for English speech recognition\n',1,NULL,NULL,NULL,NULL),
('Intent_function_call','Intent','function_call','Function Call Intent Recognition',1,1,'{\"type\": \"function_call\"}',NULL,'Function Call Intent Recognition Configuration Instructions:\n1. Uses LLM function_call capability for intent recognition\n2. Requires the selected LLM to support function_call\n3. Calls tools on demand, fast processing speed',3,NULL,NULL,NULL,NULL),
('Intent_intent_llm','Intent','intent_llm','LLM Intent Recognition',0,0,'{\"llm\": \"LLM_OpenAILLM\", \"type\": \"intent_llm\"}',NULL,'LLM Intent Recognition Configuration Instructions:\n1. Uses independent LLM for intent recognition\n2. By default uses selected_module.LLM model\n3. Can configure to use independent LLM (such as OpenAI LLM)\n4. Strong generalization but increases processing time\nConfiguration Instructions:\n1. Specify the LLM model to use in the llm field\n2. If not specified, uses selected_module.LLM model',2,NULL,NULL,NULL,NULL),
('Intent_nointent','Intent','nointent','No Intent Recognition',0,0,'{\"type\": \"nointent\"}',NULL,'No Intent Recognition Configuration Instructions:\n1. No intent recognition performed\n2. All conversations directly passed to LLM for processing\n3. No additional configuration required\n4. Suitable for simple conversation scenarios',1,NULL,NULL,NULL,NULL),
('LLM_DifyLLM','LLM','DifyLLM','Dify',0,0,'{\"mode\": \"chat-messages\", \"type\": \"dify\", \"api_key\": \"your api_key\", \"base_url\": \"https://api.dify.ai/v1\"}','https://cloud.dify.ai/','Dify Configuration Instructions:\n1. Visit https://cloud.dify.ai/\n2. Register and Get API Key\n3. Fill in configuration file\n4. Supports multiple Conversation Modes: workflows/run, chat-messages, completion-messages\n5. Role definitions set in platform will be invalid, need to set in Dify console\nNote: Recommend using locally deployed Dify Interface for better performance',7,NULL,NULL,NULL,NULL),
('LLM_GeminiLLM','LLM','GeminiLLM','Google Gemini',0,0,'{\"type\": \"gemini\", \"api_key\": \"your api_key\", \"http_proxy\": \"\", \"model_name\": \"gemini-2.0-flash\", \"https_proxy\": \"\"}','https://aistudio.google.com/apikey','Gemini Configuration Instructions:\n1. Use Google Gemini API service\n2. Current configuration uses gemini-2.0-flash model\n3. Requires network connection\n4. Supports proxy configuration\nApplication Steps:\n1. Visit https://aistudio.google.com/apikey\n2. Create API Key\n3. Fill in configuration file\nNote: Please comply with local regulations regarding AI services',8,NULL,NULL,NULL,NULL),
('LLM_LMStudioLLM','LLM','LMStudioLLM','LM Studio',0,0,'{\"type\": \"openai\", \"api_key\": \"lm-studio\", \"base_url\": \"http://localhost:1234/v1\", \"model_name\": \"llama3.1:8b\"}','https://lmstudio.ai/','LM Studio Configuration Instructions:\n1. Use locally deployed LM Studio service\n2. Current configuration uses llama3.1:8b model\n3. Local inference, no network connection required\n4. Need to download models in advance\nDeployment Steps:\n1. Install LM Studio\n2. Download models from community\n3. Ensure service runs on http://localhost:1234/v1',10,NULL,NULL,NULL,NULL),
('LLM_OpenAILLM','LLM','OpenAILLM','OpenAI GPT',1,1,'{\"type\": \"openai\", \"api_key\": \"your_api_key\", \"model_name\": \"gpt-4o-mini\", \"temperature\": 0.7, \"max_tokens\": 500}','https://platform.openai.com/api-keys','OpenAI Configuration Instructions:\n1. Visit https://platform.openai.com/api-keys\n2. Get API Key\n3. Fill in configuration file',1,NULL,NULL,NULL,NULL),
('LLM_OllamaLLM','LLM','OllamaLLM','Ollama Local Model',0,0,'{\"type\": \"ollama\", \"base_url\": \"http://localhost:11434\", \"model_name\": \"llama3.1\"}','https://ollama.com/','Ollama Configuration Instructions:\n1. Install Ollama service\n2. Run command: ollama pull llama3.1\n3. Ensure service runs on http://localhost:11434',2,NULL,NULL,NULL,NULL),
('LLM_XinferenceLLM','LLM','XinferenceLLM','Xinference Large Model',0,0,'{\"type\": \"xinference\", \"base_url\": \"http://localhost:9997\", \"model_name\": \"llama3.1:8b\"}','https://github.com/xorbitsai/inference','Xinference Configuration Instructions:\n1. Use locally deployed Xinference service\n2. Current configuration uses llama3.1:8b model\n3. Local inference, no network connection required\n4. Need to start corresponding model in advance\nDeployment Steps:\n1. Install Xinference\n2. Start service and load model\n3. Ensure service runs on http://localhost:9997',12,NULL,NULL,NULL,NULL),
('LLM_XinferenceSmallLLM','LLM','XinferenceSmallLLM','Xinference Small Model',0,0,'{\"type\": \"xinference\", \"base_url\": \"http://localhost:9997\", \"model_name\": \"llama3.1:3b\"}','https://github.com/xorbitsai/inference','Xinference Small Model Configuration Instructions:\n1. Use locally deployed Xinference service\n2. Current configuration uses llama3.1:3b model\n3. Local inference, no network connection required\n4. Used for intent recognition\nDeployment Steps:\n1. Install Xinference\n2. Start service and load model\n3. Ensure service runs on http://localhost:9997',13,NULL,NULL,NULL,NULL),
('Memory_mem_local_short','Memory','mem_local_short','Local Short Memory',1,1,'{\"llm\": \"LLM_OpenAILLM\", \"type\": \"mem_local_short\"}',NULL,'Local Short Memory Configuration Instructions:\n1. Use local storage to save conversation history\n2. Summarize conversation content through selected_module LLM\n3. Data saved locally, not uploaded to server\n4. Suitable for privacy-focused scenarios\n5. No additional configuration required',2,NULL,NULL,NULL,NULL),
('Memory_mem0ai','Memory','mem0ai','Mem0AI Memory',0,0,'{\"type\": \"mem0ai\", \"api_key\": \"your api_key\"}','https://app.mem0.ai/dashboard/api-keys','Mem0AI Memory Configuration Instructions:\n1. Use Mem0AI service to save conversation history\n2. Need API Key\n3. Requires network connection\n4. 1000 free calls per month\nApplication Steps:\n1. Visit https://app.mem0.ai/dashboard/api-keys\n2. Get API Key\n3. Fill in configuration file',3,NULL,NULL,NULL,NULL),
('Memory_nomem','Memory','nomem','No Memory',0,0,'{\"type\": \"nomem\"}',NULL,'No Memory Configuration Instructions:\n1. Do not save conversation history\n2. Each conversation is independent\n3. No additional configuration required\n4. Suitable for high privacy requirement scenarios',1,NULL,NULL,NULL,NULL),
('TTS_CustomTTS','TTS','CustomTTS','Custom TTS',0,1,'{\"url\": \"http://127.0.0.1:9880/tts\", \"type\": \"custom\", \"format\": \"wav\", \"params\": {}, \"headers\": {}, \"output_dir\": \"tmp/\"}',NULL,'Custom TTS Configuration Instructions:\n1. Custom TTS interface service with configurable request parameters\n2. Can integrate with various TTS services\n3. Example with KokoroTTS deployment\n4. CPU only: docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest\n5. GPU: docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest\nConfiguration:\n1. Configure request parameters in params using JSON format\n   Example KokoroTTS: { \"input\": \"{prompt_text}\", \"speed\": 1, \"voice\": \"zm_yunxi\", \"stream\": true, \"download_format\": \"mp3\", \"response_format\": \"mp3\", \"return_download_link\": true }\n2. Configure request headers in headers\n3. Set audio format',14,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS','TTS','EdgeTTS','Edge TTS',1,1,'{\"type\": \"edge\", \"voice\": \"en-US-AriaNeural\", \"output_dir\": \"tmp/\"}','https://github.com/rany2/edge-tts','EdgeTTS Configuration Instructions:\n1. Uses Microsoft Edge TTS service\n2. Supports multiple languages and voices\n3. Free to use, no registration required\n4. Requires network connection\n5. Output files saved in tmp/ directory',1,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS','TTS','OpenAITTS','OpenAI TTS',0,1,'{\"type\": \"openai\", \"model\": \"tts-1\", \"speed\": 1, \"voice\": \"onyx\", \"api_key\": \"your_api_key\", \"api_url\": \"https://api.openai.com/v1/audio/speech\", \"output_dir\": \"tmp/\"}','https://platform.openai.com/api-keys','OpenAI TTS Configuration Instructions:\n1. Need to get API key from OpenAI platform\n2. Supports multiple voices, current config uses onyx\n3. Requires network connection\n4. Output files saved in tmp/ directory\nApplication Steps:\n1. Visit https://platform.openai.com/api-keys to get API key\n2. Fill in configuration file\nNote: Proxy may be required depending on your location',13,NULL,NULL,NULL,NULL),
('VAD_SileroVAD','VAD','SileroVAD','Voice Activity Detection',1,1,'{\"type\": \"silero\", \"model_dir\": \"models/snakers4_silero-vad\", \"threshold\": 0.5, \"min_silence_duration_ms\": 700}','https://github.com/snakers4/silero-vad','SileroVAD Configuration Instructions:\n1. Uses SileroVAD model for voice activity detection\n2. Local inference, no network connection required\n3. Need to download model files to models/snakers4_silero-vad directory\n4. Configurable parameters:\n   - threshold: 0.5 (voice detection threshold)\n   - min_silence_duration_ms: 700 (minimum silence duration in milliseconds)\n5. If speech pauses are longer, you can increase min_silence_duration_ms value',1,NULL,NULL,NULL,NULL),
('VLLM_GeminiVLLM','VLLM','GeminiVLLM','Google Gemini Vision AI',0,1,'{\"type\": \"gemini\", \"api_key\": \"your_api_key\", \"model_name\": \"gemini-1.5-pro\"}','https://makersuite.google.com/app/apikey','Gemini Vision AI Configuration Instructions:\n1. Visit https://makersuite.google.com/app/apikey\n2. Create API key\n3. Fill in configuration file',1,NULL,NULL,NULL,NULL),
('VLLM_OpenAILLMVLLM','VLLM','OpenAILLMVLLM','OpenAI Vision Model',1,1,'{\"type\": \"openai\", \"api_key\": \"your_api_key\", \"model_name\": \"gpt-4o\"}','https://platform.openai.com/api-keys','OpenAI Vision Model Configuration Instructions:\n1. Visit https://platform.openai.com/api-keys\n2. Get API key\n3. Fill in configuration file',2,NULL,NULL,NULL,NULL);

--
-- Table structure for table `ai_model_provider`
--

CREATE TABLE `ai_model_provider` (
  `id` varchar(32) NOT NULL COMMENT 'Primary key',
  `model_type` varchar(20) DEFAULT NULL COMMENT 'Model type (Memory/ASR/VAD/LLM/TTS)',
  `provider_code` varchar(50) DEFAULT NULL COMMENT 'Provider type',
  `name` varchar(50) DEFAULT NULL COMMENT 'Provider name',
  `fields` json DEFAULT NULL COMMENT 'Provider field list (JSON format)',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_model_provider_model_type` (`model_type`) COMMENT 'Model type index for quick lookup of all provider information under specific types'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Model configuration table';

--
-- Dumping data for table `ai_model_provider`
--

INSERT INTO `ai_model_provider` VALUES ('SYSTEM_ASR_GroqASR','ASR','openai','Groq Speech Recognition','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',10,1,'2025-09-25 15:16:45',1,'2025-09-25 15:16:45'),
('SYSTEM_ASR_OpenaiASR','ASR','openai','OpenAI Speech Recognition','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',9,1,'2025-09-25 15:16:45',1,'2025-09-25 15:16:45'),
('SYSTEM_ASR_SherpaASR','ASR','sherpa_onnx_local','SherpaASR Speech Recognition','[{\"key\": \"model_dir\", \"type\": \"string\", \"label\": \"Model Directory\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',2,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_ASR_VoskASR','ASR','vosk','VOSK Offline Speech Recognition','[{\"key\": \"model_path\", \"type\": \"string\", \"label\": \"Model Path\", \"default\": \"models/vosk/vosk-model-en-us-0.22\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',1,1,'2025-09-25 15:16:45',1,'2025-09-25 15:16:45'),
('SYSTEM_Intent_function_call','Intent','function_call','Function Call Intent Recognition','[]',3,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_Intent_intent_llm','Intent','intent_llm','LLM Intent Recognition','[{\"key\": \"llm\", \"type\": \"string\", \"label\": \"LLM Model\"}]',2,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_Intent_nointent','Intent','nointent','No Intent Recognition','[]',1,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_dify','LLM','dify','Dify Interface','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"mode\", \"type\": \"string\", \"label\": \"Conversation Mode\"}]',4,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_fastgpt','LLM','fastgpt','FastGPT Interface','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"variables\", \"type\": \"dict\", \"label\": \"Variables\", \"dict_name\": \"variables\"}]',7,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_gemini','LLM','gemini','Gemini Interface','[{\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"http_proxy\", \"type\": \"string\", \"label\": \"HTTP Proxy\"}, {\"key\": \"https_proxy\", \"type\": \"string\", \"label\": \"HTTPS Proxy\"}]',5,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_ollama','LLM','ollama','Ollama Interface','[{\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Service Address\"}]',3,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_openai','LLM','openai','OpenAI Interface','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"temperature\", \"type\": \"number\", \"label\": \"Temperature\"}, {\"key\": \"max_tokens\", \"type\": \"number\", \"label\": \"Max Tokens\"}, {\"key\": \"top_p\", \"type\": \"number\", \"label\": \"Top P Value\"}, {\"key\": \"top_k\", \"type\": \"number\", \"label\": \"Top K Value\"}, {\"key\": \"frequency_penalty\", \"type\": \"number\", \"label\": \"Frequency Penalty\"}]',1,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_LLM_xinference','LLM','xinference','Xinference Interface','[{\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Service Address\"}]',8,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_Memory_mem_local_short','Memory','mem_local_short','Local Short Memory','[{\"key\": \"llm\", \"type\": \"string\", \"label\": \"LLM Model\"}]',3,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_Memory_mem0ai','Memory','mem0ai','Mem0AI Memory','[{\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}]',1,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_Memory_nomem','Memory','nomem','No Memory','[]',2,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_PLUGIN_HA_GET_STATE','Plugin','hass_get_state','HomeAssistant Device Status Query','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"HA Server Address\", \"default\": \"http://homeassistant.local:8123\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"HA API Access Token\", \"default\": \"your home assistant api access token\"}, {\"key\": \"devices\", \"type\": \"array\", \"label\": \"Device List (Name,Entity ID;...)\", \"default\": \"Living Room,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;Bedroom,Table Lamp,switch.iot_cn_831898993_socn1_on_p_2_1\"}]',50,0,'2025-09-25 15:16:45',0,'2025-09-25 15:16:45'),
('SYSTEM_PLUGIN_HA_PLAY_MUSIC','Plugin','hass_play_music','HomeAssistant Music Playback','[]',70,0,'2025-09-25 15:16:45',0,'2025-09-25 15:16:45'),
('SYSTEM_PLUGIN_HA_SET_STATE','Plugin','hass_set_state','HomeAssistant Device Status Modification','[]',60,0,'2025-09-25 15:16:45',0,'2025-09-25 15:16:45'),
('SYSTEM_PLUGIN_MUSIC','Plugin','play_music','Server Music Playback','[]',20,0,'2025-09-25 15:16:45',0,'2025-09-25 15:16:45'),
('SYSTEM_PLUGIN_WEATHER','Plugin','get_weather','Weather Service','[{\"key\": \"api_key\", \"type\": \"string\", \"label\": \"OpenWeatherMap API Key\", \"default\": \"your_openweathermap_api_key\", \"description\": \"Get your free API key at https://openweathermap.org/api. Free tier: 1000 calls/day.\"}, {\"key\": \"default_location\", \"type\": \"string\", \"label\": \"Default Location\", \"default\": \"New York\", \"description\": \"Default location when no location is specified by user.\"}]',10,0,'2025-09-25 15:16:45',0,'2025-09-25 15:16:45'),
('SYSTEM_TTS_edge','TTS','edge','Edge TTS','[{\"key\": \"voice\", \"type\": \"string\", \"label\": \"Voice\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',1,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_TTS_openai','TTS','openai','OpenAI TTS','[{\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"api_url\", \"type\": \"string\", \"label\": \"API URL\"}, {\"key\": \"model\", \"type\": \"string\", \"label\": \"Model\"}, {\"key\": \"voice\", \"type\": \"string\", \"label\": \"Voice\"}, {\"key\": \"speed\", \"type\": \"number\", \"label\": \"Speed\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',11,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_VAD_SileroVAD','VAD','silero','SileroVAD Voice Activity Detection','[{\"key\": \"threshold\", \"type\": \"number\", \"label\": \"Detection Threshold\"}, {\"key\": \"model_dir\", \"type\": \"string\", \"label\": \"Model Directory\"}, {\"key\": \"min_silence_duration_ms\", \"type\": \"number\", \"label\": \"Minimum Silence Duration\"}]',1,1,'2025-06-05 16:53:45',1,'2025-06-05 16:53:45'),
('SYSTEM_VLLM_openai','VLLM','openai','OpenAI Interface','[{\"key\": \"base_url\", \"type\": \"string\", \"label\": \"Base URL\"}, {\"key\": \"model_name\", \"type\": \"string\", \"label\": \"Model Name\"}, {\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}]',9,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
('SYSTEM_PLUGIN_NEWS','Plugin','get_news','News Service','[{\"key\": \"default_rss_url\", \"type\": \"string\", \"label\": \"Default RSS URL (Fallback)\", \"default\": \"https://feeds.reuters.com/reuters/worldNews\", \"description\": \"Fallback RSS URL when built-in sources fail. Built-in sources include Reuters, CNN, BBC, Guardian, TechCrunch and more.\"}]',31,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47');

--
-- Table structure for table `ai_ota`
--

CREATE TABLE `ai_ota` (
  `id` varchar(32) NOT NULL COMMENT 'ID',
  `firmware_name` varchar(100) DEFAULT NULL COMMENT 'Firmware name',
  `type` varchar(50) DEFAULT NULL COMMENT 'Firmware type',
  `version` varchar(50) DEFAULT NULL COMMENT 'Version number',
  `size` bigint DEFAULT NULL COMMENT 'File size (bytes)',
  `remark` varchar(500) DEFAULT NULL COMMENT 'Remarks/description',
  `firmware_path` varchar(255) DEFAULT NULL COMMENT 'Firmware path',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort order',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Firmware information table';

--
-- Dumping data for table `ai_ota`
--


--
-- Table structure for table `ai_tts_voice`
--

CREATE TABLE `ai_tts_voice` (
  `id` varchar(32) NOT NULL COMMENT 'Primary key',
  `tts_model_id` varchar(32) DEFAULT NULL COMMENT 'Corresponding TTS model primary key',
  `name` varchar(20) DEFAULT NULL COMMENT 'Voice name',
  `tts_voice` varchar(50) DEFAULT NULL COMMENT 'Voice code',
  `languages` varchar(50) DEFAULT NULL COMMENT 'Language',
  `voice_demo` varchar(500) DEFAULT NULL COMMENT 'Voice demo',
  `remark` varchar(255) DEFAULT NULL COMMENT 'Remarks',
  `reference_audio` varchar(500) DEFAULT NULL COMMENT 'Reference audio path',
  `reference_text` varchar(500) DEFAULT NULL COMMENT 'Reference text',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_ai_tts_voice_tts_model_id` (`tts_model_id`) COMMENT 'TTS model primary key index for quick lookup of voice information for corresponding models'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='TTS voice table';

--
-- Dumping data for table `ai_tts_voice`
--

INSERT INTO `ai_tts_voice` VALUES 
-- EdgeTTS Voices
('TTS_EdgeTTS_0001','TTS_EdgeTTS','Jenny','en-US-JennyNeural','American English',NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0002','TTS_EdgeTTS','Guy','en-US-GuyNeural','American English',NULL,NULL,NULL,NULL,2,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0003','TTS_EdgeTTS','Aria','en-US-AriaNeural','American English',NULL,NULL,NULL,NULL,3,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0004','TTS_EdgeTTS','Davis','en-US-DavisNeural','American English',NULL,NULL,NULL,NULL,4,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0005','TTS_EdgeTTS','Emma','en-GB-EmmaNeural','British English',NULL,NULL,NULL,NULL,5,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0006','TTS_EdgeTTS','Ryan','en-GB-RyanNeural','British English',NULL,NULL,NULL,NULL,6,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0007','TTS_EdgeTTS','Libby','en-GB-LibbyNeural','British English',NULL,NULL,NULL,NULL,7,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0008','TTS_EdgeTTS','Sonia','en-GB-SoniaNeural','British English',NULL,NULL,NULL,NULL,8,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0009','TTS_EdgeTTS','Natasha','en-AU-NatashaNeural','Australian English',NULL,NULL,NULL,NULL,9,NULL,NULL,NULL,NULL),
('TTS_EdgeTTS_0010','TTS_EdgeTTS','William','en-AU-WilliamNeural','Australian English',NULL,NULL,NULL,NULL,10,NULL,NULL,NULL,NULL),
-- OpenAITTS Voices
('TTS_OpenAITTS_0001','TTS_OpenAITTS','Alloy','alloy','American English',NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS_0002','TTS_OpenAITTS','Echo','echo','American English',NULL,NULL,NULL,NULL,2,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS_0003','TTS_OpenAITTS','Fable','fable','British English',NULL,NULL,NULL,NULL,3,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS_0004','TTS_OpenAITTS','Onyx','onyx','American English',NULL,NULL,NULL,NULL,4,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS_0005','TTS_OpenAITTS','Nova','nova','American English',NULL,NULL,NULL,NULL,5,NULL,NULL,NULL,NULL),
('TTS_OpenAITTS_0006','TTS_OpenAITTS','Shimmer','shimmer','American English',NULL,NULL,NULL,NULL,6,NULL,NULL,NULL,NULL);

--
-- Table structure for table `ai_voiceprint`
--

CREATE TABLE `ai_voiceprint` (
  `id` varchar(32) NOT NULL COMMENT 'Voice print unique identifier',
  `name` varchar(64) DEFAULT NULL COMMENT 'Voice print name',
  `user_id` bigint DEFAULT NULL COMMENT 'User ID (associated with user table)',
  `agent_id` varchar(32) DEFAULT NULL COMMENT 'Associated agent ID',
  `agent_code` varchar(36) DEFAULT NULL COMMENT 'Associated agent code',
  `agent_name` varchar(36) DEFAULT NULL COMMENT 'Associated agent name',
  `description` varchar(255) DEFAULT NULL COMMENT 'Voice print description',
  `embedding` longtext COMMENT 'Voice print feature vector (JSON array format)',
  `memory` text COMMENT 'Associated memory data',
  `sort` int unsigned DEFAULT '0' COMMENT 'Sort weight',
  `creator` bigint DEFAULT NULL COMMENT 'Creator ID',
  `created_at` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater ID',
  `updated_at` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Voice print recognition table';

--
-- Dumping data for table `ai_voiceprint`
--


--
-- Table structure for table `sys_dict_data`
--

CREATE TABLE `sys_dict_data` (
  `id` bigint NOT NULL COMMENT 'ID',
  `dict_type_id` bigint NOT NULL COMMENT 'Dictionary type ID',
  `dict_label` varchar(255) NOT NULL COMMENT 'Dictionary label',
  `dict_value` varchar(255) DEFAULT NULL COMMENT 'Dictionary value',
  `remark` varchar(255) DEFAULT NULL COMMENT 'Remarks',
  `sort` int unsigned DEFAULT NULL COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dict_type_value` (`dict_type_id`,`dict_value`),
  KEY `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Dictionary data';

--
-- Dumping data for table `sys_dict_data`
--

INSERT INTO `sys_dict_data` VALUES (101001,101,'Breadboard New Wiring (WiFi)','bread-compact-wifi','Breadboard New Wiring (WiFi)',1,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101002,101,'Breadboard New Wiring (WiFi) + LCD','bread-compact-wifi-lcd','Breadboard New Wiring (WiFi) + LCD',2,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101003,101,'Breadboard New Wiring (ML307 AT)','bread-compact-ml307','Breadboard New Wiring (ML307 AT)',3,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101004,101,'Breadboard (WiFi) ESP32 DevKit','bread-compact-esp32','Breadboard (WiFi) ESP32 DevKit',4,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101005,101,'Breadboard (WiFi+ LCD) ESP32 DevKit','bread-compact-esp32-lcd','Breadboard (WiFi+ LCD) ESP32 DevKit',5,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101006,101,'DFRobot Xingkong Board k10','df-k10','DFRobot Xingkong Board k10',6,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101007,101,'ESP32 CGC','esp32-cgc','ESP32 CGC',7,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101008,101,'ESP BOX 3','esp-box-3','ESP BOX 3',8,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101009,101,'ESP BOX','esp-box','ESP BOX',9,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101010,101,'ESP BOX Lite','esp-box-lite','ESP BOX Lite',10,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101011,101,'Kevin Box 1','kevin-box-1','Kevin Box 1',11,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101012,101,'Kevin Box 2','kevin-box-2','Kevin Box 2',12,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101013,101,'Kevin C3','kevin-c3','Kevin C3',13,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101014,101,'Kevin SP V3 Development Board','kevin-sp-v3-dev','Kevin SP V3 Development Board',14,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101015,101,'Kevin SP V4 Development Board','kevin-sp-v4-dev','Kevin SP V4 Development Board',15,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101016,101,'Yu Ying Technology 3.13LCD Development Board','kevin-yuying-313lcd','Yu Ying Technology 3.13LCD Development Board',16,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101017,101,'LCSC Practical ESP32-S3 Development Board','lichuang-dev','LCSC Practical ESP32-S3 Development Board',17,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101018,101,'LCSC Practical ESP32-C3 Development Board','lichuang-c3-dev','LCSC Practical ESP32-C3 Development Board',18,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101019,101,'Magic Button Magiclick_2.4','magiclick-2p4','Magic Button Magiclick_2.4',19,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101020,101,'Magic Button Magiclick_2.5','magiclick-2p5','Magic Button Magiclick_2.5',20,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101021,101,'Magic Button Magiclick_C3','magiclick-c3','Magic Button Magiclick_C3',21,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101022,101,'Magic Button Magiclick_C3_v2','magiclick-c3-v2','Magic Button Magiclick_C3_v2',22,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101023,101,'M5Stack CoreS3','m5stack-core-s3','M5Stack CoreS3',23,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101024,101,'AtomS3 + Echo Base','atoms3-echo-base','AtomS3 + Echo Base',24,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101025,101,'AtomS3R + Echo Base','atoms3r-echo-base','AtomS3R + Echo Base',25,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101026,101,'AtomS3R CAM/M12 + Echo Base','atoms3r-cam-m12-echo-base','AtomS3R CAM/M12 + Echo Base',26,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101027,101,'AtomMatrix + Echo Base','atommatrix-echo-base','AtomMatrix + Echo Base',27,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101028,101,'Xia Ge Mini C3','xmini-c3','Xia Ge Mini C3',28,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101029,101,'ESP32S3_KORVO2_V3 Development Board','esp32s3-korvo2-v3','ESP32S3_KORVO2_V3 Development Board',29,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101030,101,'ESP-SparkBot Development Board','esp-sparkbot','ESP-SparkBot Development Board',30,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101031,101,'ESP-Spot-S3','esp-spot-s3','ESP-Spot-S3',31,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101032,101,'Waveshare ESP32-S3-Touch-AMOLED-1.8','esp32-s3-touch-amoled-1.8','Waveshare ESP32-S3-Touch-AMOLED-1.8',32,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101033,101,'Waveshare ESP32-S3-Touch-LCD-1.85C','esp32-s3-touch-lcd-1.85c','Waveshare ESP32-S3-Touch-LCD-1.85C',33,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101034,101,'Waveshare ESP32-S3-Touch-LCD-1.85','esp32-s3-touch-lcd-1.85','Waveshare ESP32-S3-Touch-LCD-1.85',34,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101035,101,'Waveshare ESP32-S3-Touch-LCD-1.46','esp32-s3-touch-lcd-1.46','Waveshare ESP32-S3-Touch-LCD-1.46',35,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101036,101,'Waveshare ESP32-S3-Touch-LCD-3.5','esp32-s3-touch-lcd-3.5','Waveshare ESP32-S3-Touch-LCD-3.5',36,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101037,101,'Tudouzi','tudouzi','Tudouzi',37,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101038,101,'LILYGO T-Circle-S3','lilygo-t-circle-s3','LILYGO T-Circle-S3',38,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101039,101,'LILYGO T-CameraPlus-S3','lilygo-t-cameraplus-s3','LILYGO T-CameraPlus-S3',39,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101040,101,'Movecall Moji Xiaozhi AI Derivative','movecall-moji-esp32s3','Movecall Moji Xiaozhi AI Derivative',40,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101041,101,'Movecall CuiCan Brilliant AI Pendant','movecall-cuican-esp32s3','Movecall CuiCan Brilliant AI Pendant',41,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101042,101,'Zhengdian Atom DNESP32S3 Development Board','atk-dnesp32s3','Zhengdian Atom DNESP32S3 Development Board',42,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101043,101,'Zhengdian Atom DNESP32S3-BOX','atk-dnesp32s3-box','Zhengdian Atom DNESP32S3-BOX',43,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101044,101,'Dudu Development Board CHATX (WiFi)','du-chatx','Dudu Development Board CHATX (WiFi)',44,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101045,101,'Taiji Xiaopai ESP32S3','taiji-pi-s3','Taiji Xiaopai ESP32S3',45,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101046,101,'Wuming Technology Xingzhi 0.85 (WiFi)','xingzhi-cube-0.85tft-wifi','Wuming Technology Xingzhi 0.85 (WiFi)',46,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101047,101,'Wuming Technology Xingzhi 0.85 (ML307)','xingzhi-cube-0.85tft-ml307','Wuming Technology Xingzhi 0.85 (ML307)',47,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101048,101,'Wuming Technology Xingzhi 0.96 (WiFi)','xingzhi-cube-0.96oled-wifi','Wuming Technology Xingzhi 0.96 (WiFi)',48,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101049,101,'Wuming Technology Xingzhi 0.96 (ML307)','xingzhi-cube-0.96oled-ml307','Wuming Technology Xingzhi 0.96 (ML307)',49,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101050,101,'Wuming Technology Xingzhi 1.54 (WiFi)','xingzhi-cube-1.54tft-wifi','Wuming Technology Xingzhi 1.54 (WiFi)',50,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101051,101,'Wuming Technology Xingzhi 1.54 (ML307)','xingzhi-cube-1.54tft-ml307','Wuming Technology Xingzhi 1.54 (ML307)',51,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101052,101,'SenseCAP Watcher','sensecap-watcher','SenseCAP Watcher',52,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101053,101,'Sibo Zhilian AI Companion Box','doit-s3-aibox','Sibo Zhilian AI Companion Box',53,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(101054,101,'Yuan Kong Youth','mixgo-nova','Yuan Kong Youth',54,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(102001,102,'Mainland China','+86','Mainland China',1,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102002,102,'Hong Kong, China','+852','Hong Kong, China',2,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102003,102,'Macau, China','+853','Macau, China',3,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102004,102,'Taiwan, China','+886','Taiwan, China',4,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102005,102,'USA/Canada','+1','USA/Canada',5,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102006,102,'United Kingdom','+44','United Kingdom',6,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102007,102,'France','+33','France',7,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102008,102,'Italy','+39','Italy',8,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102009,102,'Germany','+49','Germany',9,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102010,102,'Poland','+48','Poland',10,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102011,102,'Switzerland','+41','Switzerland',11,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102012,102,'Spain','+34','Spain',12,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102013,102,'Denmark','+45','Denmark',13,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102014,102,'Malaysia','+60','Malaysia',14,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102015,102,'Australia','+61','Australia',15,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102016,102,'Indonesia','+62','Indonesia',16,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102017,102,'Philippines','+63','Philippines',17,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102018,102,'New Zealand','+64','New Zealand',18,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102019,102,'Singapore','+65','Singapore',19,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102020,102,'Thailand','+66','Thailand',20,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102021,102,'Japan','+81','Japan',21,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102022,102,'South Korea','+82','South Korea',22,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102023,102,'Vietnam','+84','Vietnam',23,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102024,102,'India','+91','India',24,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102025,102,'Pakistan','+92','Pakistan',25,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102026,102,'Nigeria','+234','Nigeria',26,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102027,102,'Bangladesh','+880','Bangladesh',27,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102028,102,'Saudi Arabia','+966','Saudi Arabia',28,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102029,102,'United Arab Emirates','+971','United Arab Emirates',29,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102030,102,'Brazil','+55','Brazil',30,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102031,102,'Mexico','+52','Mexico',31,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102032,102,'Chile','+56','Chile',32,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102033,102,'Argentina','+54','Argentina',33,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102034,102,'Egypt','+20','Egypt',34,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102035,102,'South Africa','+27','South Africa',35,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102036,102,'Kenya','+254','Kenya',36,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102037,102,'Tanzania','+255','Tanzania',37,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47'),
(102038,102,'Kazakhstan','+7','Kazakhstan',38,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47');

--
-- Table structure for table `sys_dict_type`
--

CREATE TABLE `sys_dict_type` (
  `id` bigint NOT NULL COMMENT 'ID',
  `dict_type` varchar(100) NOT NULL COMMENT 'Dictionary type',
  `dict_name` varchar(255) NOT NULL COMMENT 'Dictionary name',
  `remark` varchar(255) DEFAULT NULL COMMENT 'Remarks',
  `sort` int unsigned DEFAULT NULL COMMENT 'Sort order',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `dict_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Dictionary type';

--
-- Dumping data for table `sys_dict_type`
--

INSERT INTO `sys_dict_type` VALUES (101,'FIRMWARE_TYPE','Firmware Type','Firmware type dictionary',0,1,'2025-06-05 16:53:46',1,'2025-06-05 16:53:46'),
(102,'MOBILE_AREA','Mobile Area','Mobile area dictionary',0,1,'2025-06-05 16:53:47',1,'2025-06-05 16:53:47');

--
-- Table structure for table `sys_params`
--

CREATE TABLE `sys_params` (
  `id` bigint NOT NULL COMMENT 'ID',
  `param_code` varchar(100) DEFAULT NULL COMMENT 'Parameter code',
  `param_value` varchar(2000) DEFAULT NULL COMMENT 'Parameter value',
  `value_type` varchar(20) DEFAULT 'string' COMMENT 'Value type: string-text, number-numeric, boolean-boolean, array-array',
  `param_type` tinyint unsigned DEFAULT '1' COMMENT 'Type 0: system parameter 1: non-system parameter',
  `remark` varchar(200) DEFAULT NULL COMMENT 'Remarks',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_param_code` (`param_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Parameter management';

--
-- Dumping data for table `sys_params`
--

INSERT INTO `sys_params` VALUES (102,'server.secret','a1186299-4c43-4a71-987e-805fc9c41460','string',1,'Server secret key',NULL,NULL,NULL,NULL),
(103,'server.allow_user_register','false','boolean',1,'Whether to allow registration by non-administrators',NULL,NULL,NULL,NULL),
(104,'server.fronted_url','http://xiaozhi.server.com','string',1,'Control panel address displayed when sending six-digit verification code',NULL,NULL,NULL,NULL),
(105,'device_max_output_size','0','number',1,'Maximum daily output characters per device, 0 means unlimited',NULL,NULL,NULL,NULL),
(106,'server.websocket','null','string',1,'WebSocket address, separate multiple addresses with semicolons',NULL,NULL,NULL,NULL),
(107,'server.ota','null','string',1,'OTA address',NULL,NULL,NULL,NULL),
(108,'server.name','xiaozhi-esp32-server','string',1,'System name',NULL,NULL,NULL,NULL),
(109,'server.beian_icp_num','null','string',1,'ICP filing number, set to null to disable',NULL,NULL,NULL,NULL),
(110,'server.beian_ga_num','null','string',1,'Public security filing number, set to null to disable',NULL,NULL,NULL,NULL),
(111,'server.enable_mobile_register','false','boolean',1,'Whether to enable mobile phone registration',NULL,NULL,NULL,NULL),
(112,'server.sms_max_send_count','10','number',1,'Maximum SMS messages per phone number per day',NULL,NULL,NULL,NULL),
(118,'twilio.sms.account_sid','','string',1,'Twilio Account SID for SMS service',NULL,NULL,NULL,NULL),
(119,'twilio.sms.auth_token','','string',1,'Twilio Auth Token for SMS service',NULL,NULL,NULL,NULL),
(120,'twilio.sms.phone_number','','string',1,'Twilio phone number for sending SMS messages',NULL,NULL,NULL,NULL),
(121,'twilio.sms.template_message','Your verification code is: %s','string',1,'Twilio SMS template message with %s placeholder for verification code',NULL,NULL,NULL,NULL),
(122,'server.mcp_endpoint','null','string',1,'MCP endpoint address',NULL,NULL,NULL,NULL),
(123,'server.voice_print','null','string',1,'Voice print interface address',NULL,NULL,NULL,NULL),
(124,'server.voiceprint_similarity_threshold','0.4','string',1,'Voice print recognition similarity threshold, range 0.0-1.0, default 0.4, higher values are more strict',NULL,NULL,NULL,NULL),
(125,'server.mqtt_gateway','null','string',1,'MQTT gateway configuration',NULL,NULL,NULL,NULL),
(126,'server.mqtt_signature_key','null','string',1,'MQTT signature key configuration',NULL,NULL,NULL,NULL),
(127,'server.udp_gateway','null','string',1,'UDP gateway configuration',NULL,NULL,NULL,NULL),
(128,'server.mqtt_manager_api','null','string',1,'MQTT gateway management API address',NULL,NULL,NULL,NULL),
(201,'log.log_format','<green>{time:YYMMDD HH:mm:ss}</green>[<light-blue>{version}-{selected_module}</light-blue>][<light-blue>{extra[tag]}</light-blue>]-<level>{level}</level>-<light-green>{message}</light-green>','string',1,'Console log format',NULL,NULL,NULL,NULL),
(202,'log.log_format_file','{time:YYYY-MM-DD HH:mm:ss} - {version}_{selected_module} - {name} - {level} - {extra[tag]} - {message}','string',1,'File log format',NULL,NULL,NULL,NULL),
(203,'log.log_level','INFO','string',1,'Log level',NULL,NULL,NULL,NULL),
(204,'log.log_dir','tmp','string',1,'Log directory',NULL,NULL,NULL,NULL),
(205,'log.log_file','server.log','string',1,'Log file name',NULL,NULL,NULL,NULL),
(206,'log.data_dir','data','string',1,'Data directory',NULL,NULL,NULL,NULL),
(301,'delete_audio','true','boolean',1,'Whether to delete audio files after use',NULL,NULL,NULL,NULL),
(302,'close_connection_no_voice_time','120','number',1,'Connection timeout when no voice input (seconds)',NULL,NULL,NULL,NULL),
(303,'tts_timeout','10','number',1,'TTS request timeout (seconds)',NULL,NULL,NULL,NULL),
(304,'enable_wakeup_words_response_cache','true','boolean',1,'Whether to enable wake-up word acceleration',NULL,NULL,NULL,NULL),
(305,'enable_greeting','true','boolean',1,'Whether to enable greeting responses',NULL,NULL,NULL,NULL),
(306,'enable_stop_tts_notify','false','boolean',1,'Whether to enable end notification sound',NULL,NULL,NULL,NULL),
(307,'stop_tts_notify_voice','config/assets/tts_notify.mp3','string',1,'End notification sound file path',NULL,NULL,NULL,NULL),
(308,'exit_commands','exit;close','array',1,'Exit command list',NULL,NULL,NULL,NULL),
(309,'xiaozhi','{\n  \"type\": \"hello\",\n  \"version\": 1,\n  \"transport\": \"websocket\",\n  \"audio_params\": {\n    \"format\": \"opus\",\n    \"sample_rate\": 16000,\n    \"channels\": 1,\n    \"frame_duration\": 60\n  }\n}','json',1,'Xiaozhi type',NULL,NULL,NULL,NULL),
(310,'wakeup_words','Hello Xiaozhi;Hey Hello;Hello Assistant;Hey Assistant','array',1,'Wake-up word list for wake-up word recognition',NULL,NULL,NULL,NULL),
(500,'end_prompt.enable','true','boolean',1,'Whether to enable closing remarks',NULL,NULL,NULL,NULL),
(501,'end_prompt.prompt','Please start with "Time flies so fast" and end this conversation with emotional and reluctant words!','string',1,'End prompt',NULL,NULL,NULL,NULL);

--
-- Table structure for table `sys_user`
--

CREATE TABLE `sys_user` (
  `id` bigint NOT NULL COMMENT 'ID',
  `username` varchar(50) NOT NULL COMMENT 'Username',
  `password` varchar(100) DEFAULT NULL COMMENT 'Password',
  `super_admin` tinyint unsigned DEFAULT NULL COMMENT 'Super admin 0: no 1: yes',
  `status` tinyint DEFAULT NULL COMMENT 'Status 0: disabled 1: normal',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  `updater` bigint DEFAULT NULL COMMENT 'Updater',
  `creator` bigint DEFAULT NULL COMMENT 'Creator',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='System users';

--
-- Table structure for table `sys_user_token`
--

CREATE TABLE `sys_user_token` (
  `id` bigint NOT NULL COMMENT 'ID',
  `user_id` bigint NOT NULL COMMENT 'User ID',
  `token` varchar(100) NOT NULL COMMENT 'User token',
  `expire_date` datetime DEFAULT NULL COMMENT 'Expiration time',
  `update_date` datetime DEFAULT NULL COMMENT 'Update time',
  `create_date` datetime DEFAULT NULL COMMENT 'Creation time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='System user tokens';
