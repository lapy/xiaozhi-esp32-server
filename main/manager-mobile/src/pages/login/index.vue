<route lang="jsonc" type="page">
{
  "layout": "default",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "Login"
  }
}
</route>

<script lang="ts" setup>
import type { LoginData } from '@/api/auth'
import { computed, onMounted, ref } from 'vue'
import { login } from '@/api/auth'
import { useConfigStore } from '@/store'
import { getEnvBaseUrl } from '@/utils'
import { toast } from '@/utils/toast'

// Get distance from screen boundary to safe area
let safeAreaInsets
let systemInfo

// #ifdef MP-WEIXIN
// WeChat Mini Program uses new API
systemInfo = uni.getWindowInfo()
safeAreaInsets = systemInfo.safeArea
  ? {
      top: systemInfo.safeArea.top,
      right: systemInfo.windowWidth - systemInfo.safeArea.right,
      bottom: systemInfo.windowHeight - systemInfo.safeArea.bottom,
      left: systemInfo.safeArea.left,
    }
  : null
// #endif

// #ifndef MP-WEIXIN
// Other platforms continue to use uni API
systemInfo = uni.getSystemInfoSync()
safeAreaInsets = systemInfo.safeAreaInsets
// #endif
// Form data
const formData = ref<LoginData>({
  username: '',
  password: '',
  captcha: '',
  captchaId: '',
  areaCode: '+1',
  mobile: '',
})

// Captcha image
const captchaImage = ref('')
const loading = ref(false)

// Login method: 'username' | 'mobile'
const loginType = ref<'username' | 'mobile'>('username')

// Get config store
const configStore = useConfigStore()

// Area code selection related
const showAreaCodeSheet = ref(false)
const selectedAreaCode = ref('+1')
const selectedAreaName = ref('United States')

// Computed property: whether mobile login is enabled
const enableMobileLogin = computed(() => {
  return configStore.config.enableMobileRegister
})

// Computed property: area code list
const areaCodeList = computed(() => {
  return configStore.config.mobileAreaList || [{ name: 'United States', key: '+1' }]
})

// Switch login method
function toggleLoginType() {
  loginType.value = loginType.value === 'username' ? 'mobile' : 'username'
  // Clear input fields
  formData.value.username = ''
  formData.value.mobile = ''
}

// Open area code selection dialog
function openAreaCodeSheet() {
  showAreaCodeSheet.value = true
}

// Select area code
function selectAreaCode(item: { name: string, key: string }) {
  selectedAreaCode.value = item.key
  selectedAreaName.value = item.name
  formData.value.areaCode = item.key
  showAreaCodeSheet.value = false
}

// Close area code selection dialog
function closeAreaCodeSheet() {
  showAreaCodeSheet.value = false
}

// Navigate to registration page
function goToRegister() {
  uni.navigateTo({
    url: '/pages/register/index',
  })
}

// Generate UUID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

let skipReLaunch = false // Global or component scope

// Navigate to server settings page
function goToServerSetting() {
  uni.switchTab({
    url: '/pages/settings/index',
  })
}

// Get verification code
async function refreshCaptcha() {
  const uuid = generateUUID()
  formData.value.captchaId = uuid
  captchaImage.value = `${getEnvBaseUrl()}/user/captcha?uuid=${uuid}&t=${Date.now()}`
}

// Login
async function handleLogin() {
  // Form validation
  if (loginType.value === 'username') {
    if (!formData.value.username) {
      toast.warning('Please enter a username')
      return
    }
  }
  else {
    if (!formData.value.mobile) {
      toast.warning('Please enter a phone number')
      return
    }
    // Phone number format validation
    const phoneRegex = /^1[3-9]\d{9}$/
    if (!phoneRegex.test(formData.value.mobile)) {
      toast.warning('Please enter a valid phone number')
      return
    }
  }
  if (!formData.value.password) {
    toast.warning('Please enter a password')
    return
  }
  if (!formData.value.captcha) {
    toast.warning('Please enter the verification code')
    return
  }

  try {
    loading.value = true

    // Build login data
    const loginData = { ...formData.value }

    // If logging in with mobile, prefix area code to phone and assign to username
    if (loginType.value === 'mobile') {
      loginData.username = `${selectedAreaCode.value}${formData.value.mobile}`
    }

    const response = await login(loginData)
    // Store token
    uni.setStorageSync('token', response.token)
    uni.setStorageSync('expire', response.expire)

    toast.success('Login successful')

    // Navigate to the home page
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/index/index',
      })
    }, 1000)
  }
  catch (error: any) {
    // On login failure, refresh captcha
    refreshCaptcha()
  }
  finally {
    loading.value = false
  }
}

// Fetch captcha on page load
onLoad(() => {
  refreshCaptcha()
})

// Ensure configuration is loaded on mount
onMounted(async () => {
  if (!configStore.config.name) {
    try {
      await configStore.fetchPublicConfig()
    }
    catch (error) {
      console.error('Failed to fetch configuration:', error)
    }
  }
})
</script>

<template>
  <view class="app-container box-border h-screen w-full" :style="{ paddingTop: `${safeAreaInsets?.top}px` }">
    <view class="header">
      <view class="logo-section">
        <wd-img :width="80" :height="80" round src="/static/logo.png" class="logo" />
        <text class="welcome-text">
          Welcome back
        </text>
        <text class="subtitle">
          Please sign in to your account
        </text>
      </view>
    </view>
  
  	<!-- Server settings button at top-right -->
	<view 
	  class="server-btn" 
	  :style="{ top: `${safeAreaInsets?.top + 10}px` }" 
	  @click="goToServerSetting"
	>
	  <wd-icon name="setting" custom-class="server-icon" />
	</view>

    <view class="form-container">
      <view class="form">
        <!-- Mobile login -->
        <template v-if="loginType === 'mobile'">
          <view class="input-group">
            <view class="input-wrapper mobile-wrapper">
              <view class="area-code-selector" @click="openAreaCodeSheet">
                <text class="area-code-text">
                  {{ selectedAreaCode }}
                </text>
                <wd-icon name="arrow-down" custom-class="area-code-arrow" />
              </view>
              <view class="mobile-input-wrapper">
                <wd-input
                  v-model="formData.mobile"
                  custom-class="styled-input"
                  no-border
                  placeholder="Please enter your phone number"
                  type="number"
                  :maxlength="11"
                />
              </view>
            </view>
          </view>
        </template>

        <!-- Username login -->
        <template v-else>
          <view class="input-group">
            <view class="input-wrapper">
              <wd-input
                v-model="formData.username"
                custom-class="styled-input"
                no-border
                placeholder="Please enter your username"
              />
            </view>
          </view>
        </template>

        <view class="input-group">
          <view class="input-wrapper">
            <wd-input
              v-model="formData.password"
              custom-class="styled-input"
              no-border
              placeholder="Please enter your password"
              clearable
              show-password
              :maxlength="20"
            />
          </view>
        </view>

        <view class="input-group">
          <view class="input-wrapper captcha-wrapper">
            <wd-input
              v-model="formData.captcha"
              custom-class="styled-input"
              no-border
              placeholder="Please enter the verification code"
              :maxlength="6"
            />
            <view class="captcha-image" @click="refreshCaptcha">
              <image :src="captchaImage" class="captcha-img" />
            </view>
          </view>
        </view>

        <view class="forgot-password">
          <text class="forgot-text">
            Forgot password?
          </text>
        </view>

        <view
          class="login-btn"
          @click="handleLogin"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </view>

        <view class="register-hint">
          <text class="hint-text">
            Don't have an account?
          </text>
          <text class="register-link" @click="goToRegister">
            Register now
          </text>
        </view>

        <!-- Login method switch -->
        <view v-if="enableMobileLogin" class="login-type-switch">
          <view class="switch-tabs">
            <view
              class="switch-tab"
              :class="{ active: loginType === 'username' }"
              @click="toggleLoginType"
            >
              <wd-icon name="user" />
            </view>
            <view
              class="switch-tab"
              :class="{ active: loginType === 'mobile' }"
              @click="toggleLoginType"
            >
              <wd-icon name="phone" />
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Area code selection popup -->
    <wd-action-sheet
      v-model="showAreaCodeSheet"
      title="Select Country/Region"
      :close-on-click-modal="true"
      @close="closeAreaCodeSheet"
    >
      <view class="area-code-sheet">
        <scroll-view scroll-y class="area-code-list">
          <view
            v-for="item in areaCodeList"
            :key="item.key"
            class="area-code-item"
            :class="{ selected: selectedAreaCode === item.key }"
            @click="selectAreaCode(item)"
          >
            <view class="area-info">
              <text class="area-name">
                {{ item.name }}
              </text>
              <text class="area-code">
                {{ item.key }}
              </text>
            </view>
            <wd-icon
              v-if="selectedAreaCode === item.key"
              name="check"
              custom-class="check-icon"
            />
          </view>
        </scroll-view>
        <view class="sheet-footer">
          <wd-button
            type="primary"
            custom-class="confirm-btn"
            @click="closeAreaCodeSheet"
          >
            Confirm
          </wd-button>
        </view>
      </view>
    </wd-action-sheet>
  </view>
</template>

<style lang="scss" scoped>
.app-container {
  background: linear-gradient(145deg, #f5f8fd, #6baaff, #9ebbfc, #f5f8fd);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  min-height: 100vh;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.header {
  flex: 0 0 auto;
  min-height: 280rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15% 0 40rpx 0;

  .logo-section {
    text-align: center;

    .logo {
      margin-bottom: 20rpx;
      box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
    }

    .welcome-text {
      display: block;
      color: #ffffff;
      font-size: 40rpx;
      font-weight: 600;
      margin-bottom: 12rpx;
      text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
    }

    .subtitle {
      display: block;
      color: rgba(255, 255, 255, 0.8);
      font-size: 26rpx;
      font-weight: 400;
    }
  }
}

.form-container {
  padding: 0 40rpx 40rpx 40rpx;
  flex: 1;
  display: flex;
  align-items: flex-start;

  .form {
    width: 100%;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24rpx;
    padding: 40rpx 30rpx 30rpx 30rpx;
    backdrop-filter: blur(10rpx);
    box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.1);
    border: 1rpx solid rgba(255, 255, 255, 0.2);
    max-height: calc(100vh - 350rpx);
    overflow-y: auto;

    .input-group {
      margin-bottom: 24rpx;

      .input-wrapper {
        position: relative;
        background: #f8f9fa;
        border-radius: 16rpx;
        padding: 20rpx 16rpx;
        border: 2rpx solid #e9ecef;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;

        &:focus-within {
          border-color: #667eea;
          background: #ffffff;
          box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.1);
        }

        &.captcha-wrapper {
          .captcha-image {
            margin-left: 20rpx;
            width: 120rpx;
            height: 60rpx;
            border-radius: 8rpx;
            overflow: hidden;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #e9ecef;
            border: 1rpx solid #ddd;

            .captcha-img {
              width: 100%;
              height: 100%;
            }

            .captcha-loading {
              font-size: 20rpx;
              color: #999;
            }
          }
        }

        &.mobile-wrapper {
          padding: 0;
          background: transparent;
          border: none;
          display: flex;
          gap: 20rpx;

          .area-code-selector {
            flex: 0 0 160rpx;
            background: #f8f9fa;
            border-radius: 16rpx;
            padding: 20rpx 16rpx;
            border: 2rpx solid #e9ecef;
            height: 45rpx;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.3s ease;

            &:hover {
              border-color: #667eea;
              background: #ffffff;
              box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.1);
            }

            .area-code-text {
              font-size: 28rpx;
              color: #333333;
              font-weight: 500;
            }

            :deep(.area-code-arrow) {
              font-size: 24rpx;
              color: #999999;
              transition: transform 0.3s ease;
            }
          }

          .mobile-input-wrapper {
            flex: 1;
            background: #f8f9fa;
            border-radius: 16rpx;
            padding: 20rpx 16rpx;
            border: 2rpx solid #e9ecef;
            transition: all 0.3s ease;

            &:focus-within {
              border-color: #667eea;
              background: #ffffff;
              box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.1);
            }
          }
        }

        :deep(.styled-input) {
          background: transparent !important;
          border: none !important;
          outline: none !important;
          font-size: 32rpx;
          color: #333333;
          flex: 1;

          &::placeholder {
            color: #999999;
            font-size: 28rpx;
          }
        }
      }
    }

    .forgot-password {
      text-align: right;
      margin-bottom: 30rpx;

      .forgot-text {
        color: #667eea;
        font-size: 26rpx;
        cursor: pointer;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    .login-btn {
      width: 100%;
      height: 80rpx;
      border: none;
      border-radius: 16rpx;
      font-size: 30rpx;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 30rpx;
      box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.3);
      transition: all 0.3s ease;
      background-color: var(--wot-button-primary-bg-color, var(--wot-color-theme, #4d80f0));
      text-align: center;
      line-height: 80rpx;
      &:active {
        transform: translateY(2rpx);
        box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .register-hint {
      text-align: center;

      .hint-text {
        color: #666666;
        font-size: 26rpx;
        margin-right: 8rpx;
      }

      .register-link {
        color: #667eea;
        font-size: 26rpx;
        font-weight: 500;
        cursor: pointer;
        // text-decoration: underline;
        // &:hover {
        //   text-decoration: underline;
        // }
      }
    }

    .login-type-switch {
      margin-top: 20rpx;
      text-align: center;

      .switch-tabs {
        display: flex;
        justify-content: center;
        gap: 60rpx;
        margin-bottom: 20rpx;

        .switch-tab {
          width: 60rpx;
          height: 60rpx;
          border-radius: 50%;
          background: #f0f0f0;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s ease;
          border: 2rpx solid transparent;

          &.active {
            background: #667eea;
            color: #ffffff;
            border-color: #667eea;
            box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
          }

          :deep(.wd-icon) {
            font-size: 24rpx;
          }
        }
      }

      .switch-hint {
        font-size: 24rpx;
        color: #666666;
      }
    }
  }
}

// Area code selection popup style
.area-code-sheet {
  background: #ffffff;
  border-radius: 24rpx 24rpx 0 0;
  overflow: hidden;

  .sheet-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 40rpx 40rpx 20rpx 40rpx;
    border-bottom: 1rpx solid #f0f0f0;

    .sheet-title {
      font-size: 36rpx;
      font-weight: 600;
      color: #333333;
    }

    :deep(.close-icon) {
      font-size: 32rpx;
      color: #999999;
      cursor: pointer;
      padding: 10rpx;

      &:hover {
        color: #333333;
      }
    }
  }

  .area-code-list {
    max-height: 60vh;
    padding: 0 40rpx;

    .area-code-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 32rpx 0;
      border-bottom: 1rpx solid #f8f9fa;
      cursor: pointer;
      transition: background-color 0.3s ease;

      &:hover {
        background-color: #f8f9fa;
      }

      &.selected {
        background-color: rgba(102, 126, 234, 0.05);

        .area-name {
          color: #667eea;
          font-weight: 500;
        }

        .area-code {
          color: #667eea;
        }
      }

      .area-info {
        display: flex;
        flex-direction: column;
        gap: 8rpx;

        .area-name {
          font-size: 32rpx;
          color: #333333;
        }

        .area-code {
          font-size: 28rpx;
          color: #666666;
        }
      }

      :deep(.check-icon) {
        font-size: 32rpx;
        color: #667eea;
      }
    }
  }

  .sheet-footer {
    padding: 30rpx 40rpx 40rpx 40rpx;
    border-top: 1rpx solid #f0f0f0;

    :deep(.confirm-btn) {
      width: 100%;
      height: 88rpx;
      border-radius: 16rpx;
      font-size: 32rpx;
      font-weight: 600;
    }
  }
}
.server-btn {
  position: absolute;
  right: 20rpx;          // Right margin
  top: 40rpx;            // Slightly below top, not touching status bar
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.15); // Semi-transparent background, better look
  border-radius: 24rpx;                  // Round button
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.2); // Shadow

  &:active {
    transform: scale(0.95);
  }

  .server-icon {
    font-size: 28rpx;
    color: #FFFFFF; // White icon
  }

  &:hover {
    background: rgba(255, 255, 255, 0.25); // Hover effect
  }
}
// Area code popup styles
</style>
