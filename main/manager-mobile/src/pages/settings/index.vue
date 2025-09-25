<route lang="jsonc" type="page">{
  "layout": "default",
  "style": {
    "navigationBarTitleText": "Settings",
    "navigationStyle": "custom"
  }
}</route>

<script lang="ts" setup>
import { clearServerBaseUrlOverride, getEnvBaseUrl, getServerBaseUrlOverride, setServerBaseUrlOverride } from '@/utils'
import { isMp } from '@/utils/platform'
import { computed, onMounted, reactive, ref } from 'vue'
import { useToast } from 'wot-design-uni'

defineOptions({
  name: 'SettingsPage',
})

const toast = useToast()

// Cache information
const cacheInfo = reactive({
  storageSize: '0MB',
  imageCache: '0MB',
  dataCache: '0MB',
})

// Server address settings
const baseUrlInput = ref('')
const urlError = ref('')

// System information (reserved)
const systemInfo = computed(() => {
  const info = uni.getSystemInfoSync()
  return `${info.platform} ${info.system}`
})

// Read local override address
function loadServerBaseUrl() {
  const override = getServerBaseUrlOverride()
  baseUrlInput.value = override || getEnvBaseUrl()
}

// Get cache information
function getCacheInfo() {
  try {
    const info = uni.getStorageInfoSync()
    const totalSize = (info.currentSize || 0) / 1024 // KB to MB
    cacheInfo.storageSize = `${totalSize.toFixed(2)}MB`
  }
  catch (error) {
    console.error('Failed to get cache information:', error)
  }
}

// Validate URL format
function validateUrl() {
  urlError.value = ''

  if (!baseUrlInput.value) {
    return
  }

  if (!/^https?:\/\/.+\/xiaozhi$/.test(baseUrlInput.value)) {
    urlError.value = 'Please enter a valid server address (starting with http or https and ending with /xiaozhi)'
  }
}

// Test server address
async function testServerBaseUrl() {
  // Clear error message first
  urlError.value = ''

  if (!baseUrlInput.value || !/^https?:\/\/.+\/xiaozhi$/.test(baseUrlInput.value)) {
    return false
  }

  try {
    const response = await uni.request({
      url: `${baseUrlInput.value}/api/ping`,
      method: 'GET',
      timeout: 3000
    })

    if (response.statusCode === 200) {
      return true
    } else {
      toast.error('Invalid address, please check if server is running or network connection is normal')
      return false
    }
  } catch (error) {
    console.error('Failed to test server address:', error)
    toast.error('Invalid address, please check if server is running or network connection is normal')
    return false
  }
}

// Save server address
async function saveServerBaseUrl() {
  if (!baseUrlInput.value || !/^https?:\/\/.+\/xiaozhi$/.test(baseUrlInput.value)) {
    toast.warning('Please enter a valid server address (starting with http or https and ending with /xiaozhi)')
    return
  }

  // Test address validity
  const isServerValid = await testServerBaseUrl()
  if (!isServerValid) {
    return
  }
  setServerBaseUrlOverride(baseUrlInput.value)

  // Clear all cache after switching request address
  clearAllCacheAfterUrlChange()

  uni.showModal({
    title: 'Restart App',
    content: 'Server address saved and cache cleared, restart now to take effect?',
    confirmText: 'Restart Now',
    cancelText: 'Later',
    success: (res) => {
      if (res.confirm) {
        restartApp()
      }
      else {
        toast.success('Saved, you can manually restart the app later')
      }
    },
  })
}

// Reset to env default
function resetServerBaseUrl() {
  clearServerBaseUrlOverride()
  baseUrlInput.value = getEnvBaseUrl()

  // Clear all cache after switching request address
  clearAllCacheAfterUrlChange()

  uni.showModal({
    title: 'Restart App',
    content: 'Reset to default address and cache cleared, restart now to take effect?',
    confirmText: 'Restart Now',
    cancelText: 'Later',
    success: (res) => {
      if (res.confirm) {
        restartApp()
      }
      else {
        toast.success('Reset complete, you can manually restart the app later')
      }
    },
  })
}

// Restart app (Native app restart; other platforms return to home)
function restartApp() {
  // #ifdef APP-PLUS
  plus.runtime.restart()
  // #endif
  // #ifndef APP-PLUS
  uni.reLaunch({ url: '/pages/index/index' })
  // #endif
}

// Automatically clear all cache after switching address
function clearAllCacheAfterUrlChange() {
  try {
    // Backup runtime override address, ensure recovery after cleanup
    const preservedOverride = getServerBaseUrlOverride()

    // Completely clear all cache, including token
    uni.clearStorageSync()

    // Clear localStorage (H5 environment)
    // #ifdef H5
    if (typeof localStorage !== 'undefined') {
      localStorage.clear()
    }
    // #endif

    // Restore runtime override address (if any), need to write after cleanup is complete
    if (preservedOverride) {
      setServerBaseUrlOverride(preservedOverride)
    }

    // Re-get cache information
    getCacheInfo()
  }
  catch (error) {
    console.error('Clear cache failed:', error)
  }
}

// Clear cache
async function clearCache() {
  try {
    uni.showModal({
      title: 'Confirm Clear',
      content: 'Are you sure you want to clear all cache? This will delete all data including login status and require re-login.',
      success: (res) => {
        if (res.confirm) {
          clearAllCacheAfterUrlChange()
          toast.success('Cache cleared successfully, redirecting to login page')

          // Delayed redirect to login page
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/login/index' })
          }, 1500)
        }
      },
    })
  }
  catch (error) {
    console.error('Clear cache failed:', error)
    toast.error('Clear cache failed')
  }
}

// About us
function showAbout() {
  uni.showModal({
    title: `About ${import.meta.env.VITE_APP_TITLE}`,
    content: `${import.meta.env.VITE_APP_TITLE}\n\nCross-platform mobile management application built with Vue.js 3 + uni-app, providing device management and agent configuration for Xiaozhi ESP32 smart hardware.\n\n© 2025 xiaozhi-esp32-server`,
    title: `About Xiaozhi Control Panel`,
    content: `Xiaozhi Control Panel\n\nCross-platform mobile management application built with Vue.js 3 + uni-app, providing device management and agent configuration for Xiaozhi ESP32 smart hardware.\n\n© 2025 xiaozhi-esp32-server 0.8.3`,
    showCancel: false,
    confirmText: 'OK',
  })
}

onMounted(async () => {
  // Only load server address settings in non-mini-program environment
  if (!isMp) {
    loadServerBaseUrl()
  }
  getCacheInfo()
})
</script>

<template>
  <view class="min-h-screen bg-[#f5f7fb]">
    <wd-navbar title="Settings" placeholder safe-area-inset-top fixed />

    <view class="p-[24rpx]">
      <!-- Network settings - only show in non-mini-program environment -->
      <view v-if="!isMp" class="mb-[32rpx]">
        <view class="mb-[24rpx] flex items-center">
          <text class="text-[32rpx] text-[#232338] font-bold">
            Network Settings
          </text>
        </view>

        <view class="border border-[#eeeeee] rounded-[24rpx] bg-[#fbfbfb] p-[32rpx] overflow-hidden"
          style="box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);">
          <view class="mb-[24rpx]">
            <text class="text-[28rpx] text-[#232338] font-semibold">
              Server API Address
            </text>
            <text class="mt-[8rpx] block text-[24rpx] text-[#9d9ea3]">
              Cache will be cleared and app restarted after modification
            </text>
          </view>

          <view class="mb-[24rpx]">
            <view class="w-full rounded-[16rpx] border border-[#eeeeee] bg-[#f5f7fb] overflow-hidden">
              <wd-input v-model="baseUrlInput" type="text" clearable :maxlength="200"
                placeholder="Enter server address, e.g. https://example.com/xiaozhi"
                custom-class="!border-none !bg-transparent h-[88rpx] px-[24rpx] items-center"
                input-class="text-[28rpx] text-[#232338]" @input="validateUrl" @blur="validateUrl" />
            </view>
            <text v-if="urlError" class="mt-[8rpx] block text-[24rpx] text-[#ff4d4f]">
              {{ urlError }}
            </text>
          </view>

          <view class="flex gap-[16rpx]">
            <wd-button type="primary"
              custom-class="flex-1 h-[88rpx] rounded-[20rpx] text-[28rpx] font-semibold bg-[#336cff] border-none shadow-[0_4rpx_16rpx_rgba(51,108,255,0.3)] active:shadow-[0_2rpx_8rpx_rgba(51,108,255,0.4)] active:scale-98"
              @click="saveServerBaseUrl">
              Save Settings
            </wd-button>
            <wd-button type="default"
              custom-class="flex-1 h-[88rpx] rounded-[20rpx] text-[28rpx] font-semibold bg-white border-[#eeeeee] text-[#65686f] active:bg-[#f5f7fb]"
              @click="resetServerBaseUrl">
              Reset Default
            </wd-button>
          </view>
        </view>
      </view>

      <!-- Cache management -->
      <view class="mb-[32rpx]">
        <view class="mb-[24rpx] flex items-center">
          <text class="text-[32rpx] text-[#232338] font-bold">
            Cache Management
          </text>
        </view>

        <view class="border border-[#eeeeee] rounded-[24rpx] bg-[#fbfbfb] p-[32rpx]"
          style="box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);">
          <view class="space-y-[16rpx]">
            <!-- Cache information display, reference plugin style -->
            <view
              class="flex items-center justify-between border border-[#eeeeee] rounded-[16rpx] bg-[#f5f7fb] p-[24rpx] transition-all active:bg-[#eef3ff]">
              <view>
                <text class="text-[28rpx] text-[#232338] font-medium">
                  Total Cache Size
                </text>
                <text class="mt-[4rpx] block text-[24rpx] text-[#9d9ea3]">
                  Total application data size
                </text>
              </view>
              <text class="text-[28rpx] text-[#65686f] font-semibold">
                {{ cacheInfo.storageSize }}
              </text>
            </view>

            <!-- Clear cache button, reference plugin edit button style -->
            <view
              class="flex items-center justify-between border border-[#eeeeee] rounded-[16rpx] bg-[#f5f7fb] p-[24rpx]">
              <view>
                <text class="text-[28rpx] text-[#232338] font-medium">
                  Cache Cleanup
                </text>
                <text class="mt-[4rpx] block text-[24rpx] text-[#9d9ea3]">
                  Clear all cache data
                </text>
              </view>
              <view
                class="cursor-pointer rounded-[24rpx] bg-[rgba(255,107,107,0.1)] px-[28rpx] py-[16rpx] text-[24rpx] text-[#ff6b6b] font-semibold transition-all duration-300 active:scale-95 active:bg-[#ff6b6b] active:text-white"
                @click="clearCache">
                Clear Cache
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- Application information -->
      <view class="mb-[32rpx]">
        <view class="mb-[24rpx] flex items-center">
          <text class="text-[32rpx] text-[#232338] font-bold">
            Application Information
          </text>
        </view>

        <view class="border border-[#eeeeee] rounded-[24rpx] bg-[#fbfbfb] p-[32rpx]"
          style="box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);">
          <view
            class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[16rpx] bg-[#f5f7fb] p-[24rpx] transition-all active:bg-[#eef3ff]"
            @click="showAbout">
            <view>
              <text class="text-[28rpx] text-[#232338] font-medium">
                About Us
              </text>
              <text class="mt-[4rpx] block text-[24rpx] text-[#9d9ea3]">
                Application version and team information
              </text>
            </view>
            <wd-icon name="arrow-right" custom-class="text-[32rpx] text-[#9d9ea3]" />
          </view>
        </view>
      </view>

      <!-- Bottom safe area -->
      <!-- Bottom safe area -->
      <view style="height: env(safe-area-inset-bottom);" />
    </view>
  </view>
</template>

<style lang="scss" scoped>
// Keep consistent style with edit.vue, styles mainly controlled by class names</style>
