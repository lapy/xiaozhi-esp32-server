import { getServiceUrl } from '../api';
import RequestService from '../httpRequest';

export default {
    // Paginate voice clone resources
    getVoiceCloneList(params, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/voiceClone`)
            .method('GET')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('Failed to fetch voice clone list:', err);
                RequestService.reAjaxFun(() => {
                    this.getVoiceCloneList(params, callback);
                });
            }).send();
    },

    // Upload an audio file
    uploadVoice(formData, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/voiceClone/upload`)
            .method('POST')
            .data(formData)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('Failed to upload audio:', err);
                RequestService.reAjaxFun(() => {
                    this.uploadVoice(formData, callback);
                });
            }).send();
    },

    // Update a voice clone name
    updateName(params, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/voiceClone/updateName`)
            .method('POST')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('Failed to update voice clone name:', err);
                RequestService.reAjaxFun(() => {
                    this.updateName(params, callback);
                });
            }).send();
    },

    // Get the audio download ID
    getAudioId(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/voiceClone/audio/${id}`)
            .method('POST')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('Failed to fetch audio ID:', err);
                RequestService.reAjaxFun(() => {
                    this.getAudioId(id, callback);
                });
            }).send();
    },

    // Get the audio playback URL
    getPlayVoiceUrl(uuid) {
        return `${getServiceUrl()}/voiceClone/play/${uuid}`;
    },

    // Start voice cloning from uploaded audio
    cloneAudio(params, callback, errorCallback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/voiceClone/cloneAudio`)
            .method('POST')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .fail((res) => {
                // Callback for API-level failures
                RequestService.clearRequestTime();
                if (errorCallback) {
                    errorCallback(res);
                } else {
                    callback(res);
                }
            })
            .networkFail((err) => {
                console.error('Failed to submit clone request:', err);
                RequestService.reAjaxFun(() => {
                    this.cloneAudio(params, callback, errorCallback);
                });
            }).send();
    }
}
