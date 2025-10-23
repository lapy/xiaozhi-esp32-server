import { http } from '@/http/request/alova'

// Login interface data type
export interface LoginData {
  username: string
  password: string
  captcha: string
  captchaId: string
  areaCode?: string
  mobile?: string
}

// Login response data type
export interface LoginResponse {
  token: string
  expire: number
  clientHash: string
}

// Captcha response data type
export interface CaptchaResponse {
  captchaId: string
  captchaImage: string
}

// Get captcha
export function getCaptcha(uuid: string) {
  return http.Get<string>('/user/captcha', {
    params: { uuid },
    meta: {
      ignoreAuth: true,
      toast: false,
    },
  })
}

// User login
export function login(data: LoginData) {
  return http.Post<LoginResponse>('/user/login', data, {
    meta: {
      ignoreAuth: true,
      toast: true,
    },
  })
}

// User info response data type
export interface UserInfo {
  id: number
  username: string
  realName: string
  email: string
  mobile: string
  status: number
  superAdmin: number
}

// Public config response data type
export interface PublicConfig {
  enableMobileRegister: boolean
  version: string
  year: string
  allowUserRegister: boolean
  mobileAreaList: Array<{
    name: string
    key: string
  }>
  beianIcpNum: string
  beianGaNum: string
  name: string
}

// Get user info
export function getUserInfo() {
  return http.Get<UserInfo>('/user/info', {
    meta: {
      ignoreAuth: false,
      toast: false,
    },
  })
}

// Get public config
export function getPublicConfig() {
  return http.Get<PublicConfig>('/user/pub-config', {
    meta: {
      ignoreAuth: true,
      toast: false,
    },
  })
}

// Registration data type
export interface RegisterData {
  username: string
  password: string
  confirmPassword: string
  captcha: string
  captchaId: string
  areaCode: string
  mobile: string
  mobileCaptcha: string
}

// Send SMS verification code
export function sendSmsCode(data: {
  phone: string
  captcha: string
  captchaId: string
}) {
  return http.Post('/user/smsVerification', data, {
    meta: {
      ignoreAuth: true,
      toast: false,
    },
  })
}

// User registration
export function register(data: RegisterData) {
  return http.Post('/user/register', data, {
    meta: {
      ignoreAuth: true,
      toast: true,
    },
  })
}
