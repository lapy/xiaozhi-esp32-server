package xiaozhi.modules.voiceclone.service;

import java.util.List;
import java.util.Map;

import org.springframework.web.multipart.MultipartFile;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.voiceclone.dto.VoiceCloneDTO;
import xiaozhi.modules.voiceclone.dto.VoiceCloneResponseDTO;
import xiaozhi.modules.voiceclone.entity.VoiceCloneEntity;

/**
 * Voice-clone management service.
 */
public interface VoiceCloneService extends BaseService<VoiceCloneEntity> {

    /**
     * Query voice-clone records with pagination.
     */
    PageData<VoiceCloneEntity> page(Map<String, Object> params);

    /**
     * Save a voice-clone record.
     */
    void save(VoiceCloneDTO dto);

    /**
     * Delete records in batch.
     */
    void delete(String[] ids);

    /**
     * Query voice-clone records by user ID.
     *
     * @param userId user ID
     * @return voice-clone list
     */
    List<VoiceCloneEntity> getByUserId(Long userId);

    /**
     * Query paginated voice-clone records including model and user names.
     */
    PageData<VoiceCloneResponseDTO> pageWithNames(Map<String, Object> params);

    /**
     * Query a voice-clone record by ID including model and user names.
     */
    VoiceCloneResponseDTO getByIdWithNames(String id);

    /**
     * Query a user's voice-clone records including model names.
     */
    List<VoiceCloneResponseDTO> getByUserIdWithNames(Long userId);

    /**
     * Upload an audio file.
     */
    void uploadVoice(String id, MultipartFile voiceFile) throws Exception;

    /**
     * Update a voice-clone name.
     */
    void updateName(String id, String name);

    /**
     * Get audio data.
     */
    byte[] getVoiceData(String id);

    /**
     * Clone audio and trigger voice training through the upstream provider integration.
     *
     * @param cloneId voice-clone record ID
     */
    void cloneAudio(String cloneId);
}
