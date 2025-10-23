// Import requests from various modules
import admin from './module/admin.js'
import agent from './module/agent.js'
import device from './module/device.js'
import dict from './module/dict.js'
import model from './module/model.js'
import ota from './module/ota.js'
import timbre from "./module/timbre.js"
import user from './module/user.js'

/**
 * API address
 * Automatically reads .env.development file during development
 * Automatically reads .env.production file during compilation
 */
const DEV_API_SERVICE = process.env.VUE_APP_API_BASE_URL

/**
 * Return API URL based on development environment
 * @returns {string}
 */
export function getServiceUrl() {
    console.log('DEV_API_SERVICE:', DEV_API_SERVICE);
    console.log('process.env.VUE_APP_API_BASE_URL:', process.env.VUE_APP_API_BASE_URL);
    return DEV_API_SERVICE
}

/** Request service wrapper */
export default {
    getServiceUrl,
    user,
    admin,
    agent,
    device,
    model,
    timbre,
    ota,
    dict
}
