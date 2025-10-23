import Fly from 'flyio/dist/npm/fly';
import store from '../store/index';
import Constant from '../utils/constant';
import { goToPage, isNotNull, showDanger, showWarning } from '../utils/index';
import i18n from '../i18n/index';

const fly = new Fly()
// Set timeout
fly.config.timeout = 30000

/**
 * Request service wrapper
 */
export default {
    sendRequest,
    reAjaxFun,
    clearRequestTime
}

function sendRequest() {
    return {
        _sucCallback: null,
        _failCallback: null,
        _networkFailCallback: null,
        _method: 'GET',
        _data: {},
        _header: { 'content-type': 'application/json; charset=utf-8' },
        _url: '',
        _responseType: undefined, // New response type field
        'send'() {
            // Set language request header
            const currentLang = i18n.locale;
            // Convert language code format, zh_CN to zh-CN
            let acceptLanguage = currentLang.replace('_', '-');
            // Add default region code for English
            if (acceptLanguage === 'en') {
                acceptLanguage = 'en-US';
            }
            this._header['Accept-Language'] = acceptLanguage;
            
            if (isNotNull(store.getters.getToken)) {
                this._header.Authorization = 'Bearer ' + (JSON.parse(store.getters.getToken)).token
            }

            // Print request information
            fly.request(this._url, this._data, {
                method: this._method,
                headers: this._header,
                responseType: this._responseType
            }).then((res) => {
                const error = httpHandlerError(res, this._failCallback, this._networkFailCallback);
                if (error) {
                    return
                }

                if (this._sucCallback) {
                    this._sucCallback(res)
                }
            }).catch((res) => {
                // Print failed response
                console.log('catch', res)
                httpHandlerError(res, this._failCallback, this._networkFailCallback)
            })
            return this
        },
        'success'(callback) {
            this._sucCallback = callback
            return this
        },
        'fail'(callback) {
            this._failCallback = callback
            return this
        },
        'networkFail'(callback) {
            this._networkFailCallback = callback
            return this
        },
        'url'(url) {
            if (url) {
                url = url.replaceAll('$', '/')
            }
            this._url = url
            return this
        },
        'data'(data) {
            this._data = data
            return this
        },
        'method'(method) {
            this._method = method
            return this
        },
        'header'(header) {
            this._header = header
            return this
        },
        'showLoading'(showLoading) {
            this._showLoading = showLoading
            return this
        },
        'async'(flag) {
            this.async = flag
        },
        // New type setting method
        'type'(responseType) {
            this._responseType = responseType;
            return this;
        }
    }
}

/**
 * Info Request completion return information
 * failCallback Callback function
 * networkFailCallback Callback function
 */
// Add logs in error handling function
function httpHandlerError(info, failCallback, networkFailCallback) {

    /** Request successful, exit function. Can judge if request is successful based on project requirements. Here status 200 is considered successful */
    let networkError = false
    if (info.status === 200) {
        if (info.data.code === 'success' || info.data.code === 0 || info.data.code === undefined) {
            return networkError
        } else if (info.data.code === 401) {
            store.commit('clearAuth');
            goToPage(Constant.PAGE.LOGIN, true);
            return true
        } else {
            // Directly use backend returned internationalized message
            let errorMessage = info.data.msg;
            
            if (failCallback) {
                failCallback(info)
            } else {
                showDanger(errorMessage)
            }
            return true
        }
    }
    if (networkFailCallback) {
        networkFailCallback(info)
    } else {
        showDanger(`Network request error occurred【${info.status}】`)
    }
    return true
}

let requestTime = 0
let reAjaxSec = 2

function reAjaxFun(fn) {
    let nowTimeSec = new Date().getTime() / 1000
    if (requestTime === 0) {
        requestTime = nowTimeSec
    }
    let ajaxIndex = parseInt((nowTimeSec - requestTime) / reAjaxSec)
    if (ajaxIndex > 10) {
        showWarning('Unable to connect to server')
    } else {
        showWarning('Connecting to server(' + ajaxIndex + ')')
    }
    if (ajaxIndex < 10 && fn) {
        setTimeout(() => {
            fn()
        }, reAjaxSec * 1000)
    }
}

function clearRequestTime() {
    requestTime = 0
}