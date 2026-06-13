import type { uniappRequestAdapter } from '@alova/adapter-uniapp'
import type { IResponse } from './types'
import AdapterUniapp from '@alova/adapter-uniapp'
import { createAlova } from 'alova'
import { createServerTokenAuthentication } from 'alova/client'
import VueHook from 'alova/vue'
import { getEnvBaseUrl } from '@/utils'
import { toast } from '@/utils/toast'
import { ContentTypeEnum, ResultEnum, ShowMessage } from './enum'

/**
 * Create request instance
 */
const { onAuthRequired, onResponseRefreshToken } = createServerTokenAuthentication<
  typeof VueHook,
  typeof uniappRequestAdapter
>({
  refreshTokenOnError: {
    isExpired: (error) => {
      return error.response?.status === ResultEnum.Unauthorized
    },
    handler: async () => {
      try {
        // await authLogin();
      }
      catch (error) {
        // Switch to login page
        await uni.reLaunch({ url: '/pages/login/index' })
        throw error
      }
    },
  },
})

/**
 * Alova request instance
 */
const alovaInstance = createAlova({
  baseURL: getEnvBaseUrl(),
  ...AdapterUniapp(),
  timeout: 5000,
  statesHook: VueHook,

  beforeRequest: onAuthRequired((method) => {
    // Set default Content-Type
    method.config.headers = {
      'Content-Type': ContentTypeEnum.JSON,
      'Accept': 'application/json, text/plain, */*',
      ...method.config.headers,
    }

    const { config } = method
    const ignoreAuth = config.meta?.ignoreAuth
    console.log('ignoreAuth===>', ignoreAuth)

    // Handle authentication info
    if (!ignoreAuth) {
      const token = uni.getStorageSync('token')
      if (!token) {
        // Jump to login page
        uni.reLaunch({ url: '/pages/login/index' })
        throw new Error('[Request Error]: Not logged in')
      }
      // Add Authorization header
      method.config.headers.Authorization = `Bearer ${token}`
    }

    // Handle dynamic domain
    if (config.meta?.domain) {
      method.baseURL = config.meta.domain
      console.log('Current domain', method.baseURL)
    }
  }),

  responded: onResponseRefreshToken((response, method) => {
    const { config } = method
    const { requestType } = config
    const {
      statusCode,
      data: rawData,
      errMsg,
    } = response as UniNamespace.RequestSuccessCallbackResult

    console.log(response)

    // Handle special request types (upload/download)
    if (requestType === 'upload' || requestType === 'download') {
      return response
    }

    // Handle HTTP status code errors
    if (statusCode !== 200) {
      const errorMessage = ShowMessage(statusCode) || `HTTP request error[${statusCode}]`
      console.error('errorMessage===>', errorMessage)
      toast.error(errorMessage)
      throw new Error(`${errorMessage}：${errMsg}`)
    }

    // Handle business logic errors
    const { code, msg, data } = rawData as IResponse
    if (code !== ResultEnum.Success) {
      // Check if token is invalid
      if (code === ResultEnum.Unauthorized) {
        // Clear token and redirect to login page
        uni.removeStorageSync('token')
        uni.reLaunch({ url: '/pages/login/index' })
        throw new Error(`Request error[${code}]: ${msg}`)
      }

      if (config.meta?.toast !== false) {
        toast.warning(msg)
      }
      throw new Error(`Request error[${code}]: ${msg}`)
    }
    // Handle successful response, return business data
    return data
  }),
})

export const http = alovaInstance
