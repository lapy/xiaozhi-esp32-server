<script setup lang="ts">
import { computed, ref } from 'vue'
import { useToast } from 'wot-design-uni'

// Type definitions
interface WiFiNetwork {
  ssid: string
  rssi: number
  authmode: number
  channel: number
}

// Props
interface Props {
  selectedNetwork: WiFiNetwork | null
  password: string
}

const props = defineProps<Props>()

// Toast instance
const toast = useToast()

// Reactive data
const configuring = ref(false)

// Computed properties
const canSubmit = computed(() => {
  if (!props.selectedNetwork)
    return false
  if (props.selectedNetwork.authmode > 0 && !props.password)
    return false
  return true
})

// ESP32 connection check
async function checkESP32Connection() {
  try {
    const response = await uni.request({
      url: 'http://192.168.4.1/scan',
      method: 'GET',
      timeout: 3000,
    })
    return response.statusCode === 200
  }
  catch (error) {
    console.log('ESP32 connection check failed:', error)
    return false
  }
}

// Submit network configuration
async function submitConfig() {
  if (!props.selectedNetwork)
    return

  // Check ESP32 connection
  const connected = await checkESP32Connection()
  if (!connected) {
    toast.error('Please connect to xiaozhi hotspot first')
    return
  }

  configuring.value = true
  console.log('Start WiFi configuration:', props.selectedNetwork.ssid)

  try {
    const response = await uni.request({
      url: 'http://192.168.4.1/submit',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
      },
      data: {
        ssid: props.selectedNetwork.ssid,
        password: props.selectedNetwork.authmode > 0 ? props.password : '',
      },
      timeout: 15000,
    })

    console.log('WiFi configuration response:', response)

    if (response.statusCode === 200 && (response.data as any)?.success) {
      toast.success(`Configuration successful! Device will connect to ${props.selectedNetwork.ssid}, device will restart automatically. Please disconnect xiaozhi hotspot connection.`)
    }
    else {
      const errorMsg = (response.data as any)?.error || 'Configuration failed'
      toast.error(errorMsg)
    }
  }
  catch (error) {
    console.error('WiFi configuration failed:', error)
    toast.error('Configuration failed, please check network connection')
  }
  finally {
    configuring.value = false
  }
}
</script>

<template>
  <view class="wifi-config">
    <!-- Selected network information -->
    <view v-if="props.selectedNetwork" class="selected-network">
      <view class="network-info">
        <view class="network-name">
          Selected Network: {{ props.selectedNetwork.ssid }}
        </view>
        <view class="network-details">
          <text class="network-signal">
            Signal: {{ props.selectedNetwork.rssi }}dBm
          </text>
          <text class="network-security">
            {{ props.selectedNetwork.authmode === 0 ? 'Open Network' : 'Encrypted Network' }}
          </text>
        </view>
      </view>
    </view>

    <!-- Configuration button -->
    <view class="submit-section">
      <wd-button
        type="primary"
        size="large"
        block
        :loading="configuring"
        :disabled="!canSubmit"
        @click="submitConfig"
      >
        {{ configuring ? 'Configuring...' : 'Start WiFi Configuration' }}
      </wd-button>
    </view>

    <!-- Usage instructions -->
    <view class="help-section">
      <view class="help-title">
        WiFi Configuration Instructions
      </view>
      <view class="help-content">
        <text class="help-item">
          1. Connect phone to xiaozhi hotspot (xiaozhi-XXXXXX)
        </text>
        <text class="help-item">
          2. Select target WiFi network to configure
        </text>
        <text class="help-item">
          3. Enter WiFi password (if required)
        </text>
        <text class="help-item">
          4. Click start configuration and wait for device connection
        </text>
        <text class="help-tip">
          After successful network configuration, the device will automatically restart and connect to the target WiFi
        </text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.wifi-config {
  padding: 20rpx 0;
}

.selected-network {
  margin-bottom: 32rpx;
}

.network-info {
  padding: 24rpx;
  background-color: #f0f6ff;
  border: 1rpx solid #336cff;
  border-radius: 16rpx;
}

.network-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #232338;
  margin-bottom: 8rpx;
}

.network-details {
  display: flex;
  gap: 24rpx;
}

.network-signal,
.network-security {
  font-size: 24rpx;
  color: #65686f;
}

.submit-section {
  margin-bottom: 32rpx;
}

.help-section {
  padding: 32rpx 24rpx;
  background-color: #fbfbfb;
  border-radius: 16rpx;
  border: 1rpx solid #eeeeee;
}

.help-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #232338;
  margin-bottom: 20rpx;
}

.help-content {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.help-item {
  font-size: 24rpx;
  color: #65686f;
  line-height: 1.5;
}

.help-tip {
  font-size: 24rpx;
  color: #336cff;
  font-weight: 500;
  margin-top: 8rpx;
}
</style>
