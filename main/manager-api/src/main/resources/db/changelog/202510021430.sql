--
-- Add ElevenLabs TTS configuration support
-- Migration date: 2025-10-02 14:30
-- Author: ai_assistant
--

-- Add ElevenLabs TTS model configuration
INSERT INTO `ai_model_config` VALUES 
('TTS_ElevenLabsTTS','TTS','ElevenLabsTTS','ElevenLabs TTS',0,1,'{\"type\": \"elevenlabs\", \"api_key\": \"your_elevenlabs_api_key\", \"api_url\": \"https://api.elevenlabs.io/v1/text-to-speech\", \"voice_id\": \"21m00Tcm4TlvDq8ikWAM\", \"model_id\": \"eleven_turbo_v2_5\", \"stability\": 0.5, \"similarity_boost\": 0.5, \"style\": 0.0, \"use_speaker_boost\": true, \"optimize_streaming_latency\": 0, \"output_format\": \"mp3_44100_128\", \"output_dir\": \"tmp/\"}','https://elevenlabs.io/','ElevenLabs TTS Configuration Instructions:\n1. Get your API key from https://elevenlabs.io/\n2. High-quality AI voices with natural speech patterns\n3. Supports voice customization with stability, similarity, and style controls\n4. Uses eleven_turbo_v2_5 model for fastest generation with low latency\n5. Multiple output formats supported (MP3, PCM, etc.)\n6. Popular voice IDs included in configuration\nConfiguration:\n1. Set your API key in the api_key field\n2. Choose voice_id from available voices\n3. Adjust voice settings (stability, similarity_boost, style)\n4. Configure output format and directory',15,NULL,NULL,NULL,NULL);

-- Add ElevenLabs provider definition
INSERT INTO `ai_model_provider` VALUES 
('SYSTEM_TTS_elevenlabs','TTS','elevenlabs','ElevenLabs TTS','[{\"key\": \"api_key\", \"type\": \"string\", \"label\": \"API Key\"}, {\"key\": \"api_url\", \"type\": \"string\", \"label\": \"API URL\"}, {\"key\": \"voice_id\", \"type\": \"string\", \"label\": \"Voice ID\"}, {\"key\": \"model_id\", \"type\": \"string\", \"label\": \"Model ID\"}, {\"key\": \"stability\", \"type\": \"number\", \"label\": \"Stability\"}, {\"key\": \"similarity_boost\", \"type\": \"number\", \"label\": \"Similarity Boost\"}, {\"key\": \"style\", \"type\": \"number\", \"label\": \"Style\"}, {\"key\": \"use_speaker_boost\", \"type\": \"boolean\", \"label\": \"Use Speaker Boost\"}, {\"key\": \"optimize_streaming_latency\", \"type\": \"number\", \"label\": \"Optimize Streaming Latency\"}, {\"key\": \"output_format\", \"type\": \"string\", \"label\": \"Output Format\"}, {\"key\": \"output_dir\", \"type\": \"string\", \"label\": \"Output Directory\"}]',16,1,'2025-10-02 14:30:00',1,'2025-10-02 14:30:00');

-- Add popular ElevenLabs voices
INSERT INTO `ai_tts_voice` VALUES 
-- ElevenLabs Popular Voices
('TTS_ElevenLabs_0001','TTS_ElevenLabsTTS','Rachel','21m00Tcm4TlvDq8ikWAM','American English - Calm, Young Adult Female',NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0002','TTS_ElevenLabsTTS','Adam','pNInz6obpgDQGcFmaJgB','American English - Deep, Middle-aged Male',NULL,NULL,NULL,NULL,2,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0003','TTS_ElevenLabsTTS','Antoni','ErXwobaYiN019PkySvjV','American English - Well-rounded, Middle-aged Male',NULL,NULL,NULL,NULL,3,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0004','TTS_ElevenLabsTTS','Arnold','VR6AewLTigWG4xSOukaG','American English - Crisp, Middle-aged Male',NULL,NULL,NULL,NULL,4,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0005','TTS_ElevenLabsTTS','Bella','EXAVITQu4vr4xnSDxMaL','American English - Soft, Young Adult Female',NULL,NULL,NULL,NULL,5,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0006','TTS_ElevenLabsTTS','Domi','AZnzlk1XvdvUeBnXmlld','American English - Strong, Young Adult Female',NULL,NULL,NULL,NULL,6,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0007','TTS_ElevenLabsTTS','Elli','MF3mGyEYCl7XYWbV9V6O','American English - Emotional, Young Adult Female',NULL,NULL,NULL,NULL,7,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0008','TTS_ElevenLabsTTS','Josh','TxGEqnHWrfWFTfGW9XjX','American English - Deep, Young Adult Male',NULL,NULL,NULL,NULL,8,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0009','TTS_ElevenLabsTTS','Sam','yoZ06aMxZJJ28mfd3POQ','American English - Raspy, Young Adult Male',NULL,NULL,NULL,NULL,9,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0010','TTS_ElevenLabsTTS','Matilda','XrExE9yKIg1WjnnlVkGX','American English - Warm, Middle-aged Female',NULL,NULL,NULL,NULL,10,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0011','TTS_ElevenLabsTTS','Matthew','Yko7PKHZNXotIFUBG7I9','British English - Clear, Middle-aged Male',NULL,NULL,NULL,NULL,11,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0012','TTS_ElevenLabsTTS','James','ZQe5CqHNLWdS2F4s9BqK','Australian English - Calm, Young Adult Male',NULL,NULL,NULL,NULL,12,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0013','TTS_ElevenLabsTTS','Hope','uYXf8XasLslADfZ2MB4u','American English - Friendly, Engaging Female',NULL,NULL,NULL,NULL,13,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0014','TTS_ElevenLabsTTS','Daniel','onwK6e5U6N7xDrBOmXO','British English - Energetic, Enthusiastic Male',NULL,NULL,NULL,NULL,14,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0015','TTS_ElevenLabsTTS','Lily','pFZP5JQG7iQjIQuC4Bku','British English - Warm, Pleasant Female',NULL,NULL,NULL,NULL,15,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0016','TTS_ElevenLabsTTS','Freya','jsCqWAovK2LkecY7zXl4','American English - Confident, Professional Female',NULL,NULL,NULL,NULL,16,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0017','TTS_ElevenLabsTTS','Charlie','IK2y5XjIqaOfvMWOhSXy','Australian English - Casual, Friendly Male',NULL,NULL,NULL,NULL,17,NULL,NULL,NULL,NULL),
('TTS_ElevenLabs_0018','TTS_ElevenLabsTTS','Grace','oWAxZDx7w5VEj9dCyTzz','American English - Gentle, Soothing Female',NULL,NULL,NULL,NULL,18,NULL,NULL,NULL,NULL);
