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
const generating = ref(false)
const playing = ref(false)
const audioGenerated = ref(false)
const autoLoop = ref(true)
const audioFilePath = ref('')
const audioContext = ref<any>(null)

// AFSK modulation parameters - reference HTML file
const MARK = 1800 // Frequency for binary 1 (Hz)
const SPACE = 1500 // Frequency for binary 0 (Hz)
const SAMPLE_RATE = 44100 // Sample rate
const BIT_RATE = 100 // Bit rate (bps)
const START_BYTES = [0x01, 0x02] // Start marker
const END_BYTES = [0x03, 0x04] // End marker

// Computed properties
const canGenerate = computed(() => {
  if (!props.selectedNetwork)
    return false
  if (props.selectedNetwork.authmode > 0 && !props.password)
    return false
  return true
})

const audioLengthText = computed(() => {
  if (!props.selectedNetwork)
    return '0 seconds'
  const dataStr = `${props.selectedNetwork.ssid}\n${props.password}`
  const textBytes = stringToBytes(dataStr)
  const totalBits = (START_BYTES.length + textBytes.length + 1 + END_BYTES.length) * 8
  const duration = Math.ceil(totalBits / BIT_RATE)
  return `About ${duration} seconds`
})

// String to byte array - uniapp compatible version
function stringToBytes(str: string): number[] {
  const bytes: number[] = []
  for (let i = 0; i < str.length; i++) {
    const code = str.charCodeAt(i)
    if (code < 0x80) {
      bytes.push(code)
    }
    else if (code < 0x800) {
      bytes.push(0xC0 | (code >> 6))
      bytes.push(0x80 | (code & 0x3F))
    }
    else if (code < 0xD800 || code >= 0xE000) {
      bytes.push(0xE0 | (code >> 12))
      bytes.push(0x80 | ((code >> 6) & 0x3F))
      bytes.push(0x80 | (code & 0x3F))
    }
    else {
      // Surrogate pair handling
      i++
      const hi = code
      const lo = str.charCodeAt(i)
      const codePoint = 0x10000 + (((hi & 0x3FF) << 10) | (lo & 0x3FF))
      bytes.push(0xF0 | (codePoint >> 18))
      bytes.push(0x80 | ((codePoint >> 12) & 0x3F))
      bytes.push(0x80 | ((codePoint >> 6) & 0x3F))
      bytes.push(0x80 | (codePoint & 0x3F))
    }
  }
  return bytes
}

// Checksum calculation - reference HTML file
function checksum(data: number[]): number {
  return data.reduce((sum, b) => (sum + b) & 0xFF, 0)
}

// Byte to bit conversion - reference HTML file
function toBits(byte: number): number[] {
  const bits: number[] = []
  for (let i = 7; i >= 0; i--) {
    bits.push((byte >> i) & 1)
  }
  return bits
}

// AFSK modulation - reference HTML file algorithm
function afskModulate(bits: number[]): Float32Array {
  const samplesPerBit = SAMPLE_RATE / BIT_RATE
  const totalSamples = Math.floor(bits.length * samplesPerBit)
  const buffer = new Float32Array(totalSamples)

  for (let i = 0; i < bits.length; i++) {
    const freq = bits[i] ? MARK : SPACE
    for (let j = 0; j < samplesPerBit; j++) {
      const t = (i * samplesPerBit + j) / SAMPLE_RATE
      buffer[i * samplesPerBit + j] = Math.sin(2 * Math.PI * freq * t)
    }
  }

  return buffer
}

// Float to 16-bit PCM - reference HTML file
function floatTo16BitPCM(floatSamples: Float32Array): Uint8Array {
  const buffer = new Uint8Array(floatSamples.length * 2)
  for (let i = 0; i < floatSamples.length; i++) {
    const s = Math.max(-1, Math.min(1, floatSamples[i]))
    const val = s < 0 ? s * 0x8000 : s * 0x7FFF
    buffer[i * 2] = val & 0xFF
    buffer[i * 2 + 1] = (val >> 8) & 0xFF
  }
  return buffer
}

// Base64 encoding table
const base64Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

// Compatible base64 encoding implementation
function base64Encode(bytes: Uint8Array): string {
  let result = ''
  let i = 0

  while (i < bytes.length) {
    const a = bytes[i++]
    const b = i < bytes.length ? bytes[i++] : 0
    const c = i < bytes.length ? bytes[i++] : 0

    const bitmap = (a << 16) | (b << 8) | c

    result += base64Chars.charAt((bitmap >> 18) & 63)
    result += base64Chars.charAt((bitmap >> 12) & 63)
    result += i - 2 < bytes.length ? base64Chars.charAt((bitmap >> 6) & 63) : '='
    result += i - 1 < bytes.length ? base64Chars.charAt(bitmap & 63) : '='
  }

  return result
}

// Array to base64 encoding - compatible version
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)

  // Try to use native btoa, if not available use custom implementation
  if (typeof btoa !== 'undefined') {
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }
  else {
    return base64Encode(bytes)
  }
}

// Build WAV file - return ArrayBuffer instead of Blob
function buildWav(pcm: Uint8Array): ArrayBuffer {
  const wavHeader = new Uint8Array(44)
  const dataLen = pcm.length
  const fileLen = 36 + dataLen

  const writeStr = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      wavHeader[offset + i] = str.charCodeAt(i)
    }
  }

  const write32 = (offset: number, value: number) => {
    wavHeader[offset] = value & 0xFF
    wavHeader[offset + 1] = (value >> 8) & 0xFF
    wavHeader[offset + 2] = (value >> 16) & 0xFF
    wavHeader[offset + 3] = (value >> 24) & 0xFF
  }

  const write16 = (offset: number, value: number) => {
    wavHeader[offset] = value & 0xFF
    wavHeader[offset + 1] = (value >> 8) & 0xFF
  }

  writeStr(0, 'RIFF')
  write32(4, fileLen)
  writeStr(8, 'WAVE')
  writeStr(12, 'fmt ')
  write32(16, 16)
  write16(20, 1)
  write16(22, 1)
  write32(24, SAMPLE_RATE)
  write32(28, SAMPLE_RATE * 2)
  write16(32, 2)
  write16(34, 16)
  writeStr(36, 'data')
  write32(40, dataLen)

  // Merge header and data
  const result = new ArrayBuffer(44 + dataLen)
  const resultView = new Uint8Array(result)
  resultView.set(wavHeader)
  resultView.set(pcm, 44)

  return result
}

// Generate and play sound wave - main function
async function generateAndPlay() {
  if (!canGenerate.value || !props.selectedNetwork)
    return

  generating.value = true

  try {
    console.log('Generating ultrasonic configuration audio...')

    // Prepare network configuration data - reference HTML file format
    const dataStr = `${props.selectedNetwork.ssid}\n${props.password}`
    const textBytes = stringToBytes(dataStr)
    const fullBytes = [...START_BYTES, ...textBytes, checksum(textBytes), ...END_BYTES]

    console.log('Network config data:', { ssid: props.selectedNetwork.ssid, password: props.password })
    console.log('Data byte length:', textBytes.length)

    // Convert to bit stream
    let bits: number[] = []
    fullBytes.forEach((b) => {
      bits = bits.concat(toBits(b))
    })

    console.log('Bit stream length:', bits.length)

    // AFSK modulation - reduce sample rate to lower file size
    const reducedSampleRate = 22050 // Reduced sample rate
    const samplesPerBit = reducedSampleRate / BIT_RATE
    const totalSamples = Math.floor(bits.length * samplesPerBit)
    const floatBuf = new Float32Array(totalSamples)

    for (let i = 0; i < bits.length; i++) {
      const freq = bits[i] ? MARK : SPACE
      for (let j = 0; j < samplesPerBit; j++) {
        const t = (i * samplesPerBit + j) / reducedSampleRate
        floatBuf[i * samplesPerBit + j] = Math.sin(2 * Math.PI * freq * t) * 0.5 // Reduce volume
      }
    }

    const pcmBuf = floatTo16BitPCM(floatBuf)

    // Generate WAV file - use reduced sample rate
    const wavBuffer = buildWavOptimized(pcmBuf, reducedSampleRate)
    const base64 = arrayBufferToBase64(wavBuffer)
    const dataUri = `data:audio/wav;base64,${base64}`

    console.log('base64 length:', base64.length, 'approx', Math.round(base64.length / 1024), 'KB')

    // Check data size
    if (base64.length > 1024 * 1024) { // Over 1MB
      throw new Error('Audio file too large, please shorten SSID or password length')
    }

    audioFilePath.value = dataUri
    audioGenerated.value = true

    console.log('Audio generation successful, bit stream length:', bits.length, 'sample count:', floatBuf.length)

    toast.success('Sound wave generated successfully')

    // Delayed playback
    setTimeout(async () => {
      await playAudio()
    }, 800) // Increase delay time
  }
  catch (error) {
    console.error('Audio generation failed:', error)
    toast.error(`Sound wave generation failed: ${error.message || error}`)
  }
  finally {
    generating.value = false
  }
}

// Optimized WAV build function
function buildWavOptimized(pcm: Uint8Array, sampleRate: number): ArrayBuffer {
  const wavHeader = new Uint8Array(44)
  const dataLen = pcm.length
  const fileLen = 36 + dataLen

  const writeStr = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) {
      wavHeader[offset + i] = str.charCodeAt(i)
    }
  }

  const write32 = (offset: number, value: number) => {
    wavHeader[offset] = value & 0xFF
    wavHeader[offset + 1] = (value >> 8) & 0xFF
    wavHeader[offset + 2] = (value >> 16) & 0xFF
    wavHeader[offset + 3] = (value >> 24) & 0xFF
  }

  const write16 = (offset: number, value: number) => {
    wavHeader[offset] = value & 0xFF
    wavHeader[offset + 1] = (value >> 8) & 0xFF
  }

  writeStr(0, 'RIFF')
  write32(4, fileLen)
  writeStr(8, 'WAVE')
  writeStr(12, 'fmt ')
  write32(16, 16)
  write16(20, 1)
  write16(22, 1)
  write32(24, sampleRate) // Use passed sample rate
  write32(28, sampleRate * 2)
  write16(32, 2)
  write16(34, 16)
  writeStr(36, 'data')
  write32(40, dataLen)

  // Merge header and data
  const result = new ArrayBuffer(44 + dataLen)
  const resultView = new Uint8Array(result)
  resultView.set(wavHeader)
  resultView.set(pcm, 44)

  return result
}

// Play audio
async function playAudio() {
  if (!audioFilePath.value) {
    toast.error('Please generate audio first')
    return
  }

  try {
    // Force cleanup of all old audio instances
    await cleanupAudio()

    // Wait to ensure cleanup is complete
    await new Promise(resolve => setTimeout(resolve, 200))

    playing.value = true
    console.log('Starting ultrasonic network config audio playback')

    // Create new audio context
    const innerAudioContext = uni.createInnerAudioContext()
    audioContext.value = innerAudioContext

    // Simplified audio settings
    innerAudioContext.src = audioFilePath.value
    innerAudioContext.loop = autoLoop.value
    innerAudioContext.volume = 0.8
    innerAudioContext.autoplay = false

    // Simplified event listeners
    innerAudioContext.onPlay(() => {
      console.log('Ultrasonic audio playback started')
      toast.success('Started playing network config sound wave')
    })

    innerAudioContext.onEnded(() => {
      console.log('Ultrasonic audio playback ended')
      if (!autoLoop.value) {
        playing.value = false
        cleanupAudio()
      }
    })

    innerAudioContext.onError((error) => {
      console.error('Audio playback failed:', error)
      playing.value = false

      let errorMsg = 'Audio playback failed'
      if (error.errCode === -99) {
        errorMsg = 'Audio resource busy, please try again later'
      }
      else if (error.errCode === 10004) {
        errorMsg = 'Audio format not supported, possibly data URI issue'
      }
      else if (error.errCode === 10003) {
        errorMsg = 'Audio file error'
      }

      toast.error(errorMsg)

      cleanupAudio()
    })

    innerAudioContext.onStop(() => {
      console.log('Audio playback stopped')
      playing.value = false
    })

    // Delayed playback
    setTimeout(() => {
      if (audioContext.value) {
        console.log('Attempting to play audio, src length:', audioFilePath.value.length)
        audioContext.value.play()
      }
    }, 300)
  }
  catch (error) {
    console.error('Audio playback exception:', error)
    playing.value = false
    await cleanupAudio()
    toast.error(`Playback failed: ${error.message}`)
  }
}

// Cleanup audio resources
async function cleanupAudio() {
  if (audioContext.value) {
    try {
      audioContext.value.pause()
      audioContext.value.destroy()
      console.log('Cleanup audio context')
    }
    catch (e) {
      console.log('Cleanup audio context failed:', e)
    }
    finally {
      audioContext.value = null
    }
  }
}

// Stop playback
async function stopAudio() {
  playing.value = false
  await cleanupAudio()

  console.log('Stop ultrasonic audio playback')
  toast.success('Playback stopped')
}
</script>

<template>
  <view class="ultrasonic-config">
    <!-- Selected network information -->
    <view v-if="props.selectedNetwork" class="selected-network">
      <view class="network-info">
        <view class="network-name">
          Selected network: {{ props.selectedNetwork.ssid }}
        </view>
        <view class="network-details">
          <text class="network-signal">
            Signal: {{ props.selectedNetwork.rssi }}dBm
          </text>
          <text class="network-security">
            {{ props.selectedNetwork.authmode === 0 ? 'Open network' : 'Encrypted network' }}
          </text>
        </view>
        <view v-if="props.password" class="network-password">
          Password: {{ '*'.repeat(props.password.length) }}
        </view>
      </view>
    </view>

    <!-- Ultrasonic network configuration operations -->
    <view class="submit-section">
      <wd-button
        type="primary"
        size="large"
        block
        :loading="generating"
        :disabled="!canGenerate"
        @click="generateAndPlay"
      >
        {{ generating ? 'Generating...' : '🎵 Generate and play sound wave' }}
      </wd-button>

      <wd-button
        v-if="audioGenerated"
        type="success"
        size="large"
        block
        :loading="playing"
        @click="playAudio"
      >
        {{ playing ? 'Playing...' : '🔊 Play sound wave' }}
      </wd-button>

      <wd-button
        v-if="playing"
        type="warning"
        size="large"
        block
        @click="stopAudio"
      >
        ⏹️ Stop playback
      </wd-button>
    </view>

    <!-- Audio control options -->
    <view v-if="audioGenerated" class="audio-options">
      <view class="option-item">
        <wd-checkbox v-model="autoLoop">
          Auto loop sound wave playback
        </wd-checkbox>
      </view>
    </view>

    <!-- Audio player -->
    <view v-if="audioGenerated" class="audio-player">
      <view class="player-info">
        <text class="audio-title">
          Network config audio file
        </text>
        <text class="audio-duration">
          Duration: {{ audioLengthText }}
        </text>
      </view>
    </view>

    <!-- Usage instructions -->
    <view class="help-section">
      <view class="help-title">
        Ultrasonic Network Configuration Instructions
      </view>
      <view class="help-content">
        <text class="help-item">
          • If configuration fails, please check if WiFi password is correct network is selected and password is entered
        </text>
        <text class="help-item">
          2. Click generate and play sound wave, system will encode network config info as audio
        </text>
        <text class="help-item">
          3. Place phone close to device so device can hear the audio signal (distance 1-2 meters)
        </text>
        <text class="help-item">
          4. During audio playback, device will receive and decode network config info
        </text>
        <text class="help-item">
          5. Device will automatically connect to WiFi network after receiving signal
        </text>
        <text class="help-tip">
          Using AFSK modulation technology, transmitting data through 1800Hz and 1500Hz frequencies
        </text>
        <text class="help-tip">
          • Please ensure phone volume is set to moderate level, avoiding environmental noise interference
        </text>
      </view>
    </view>
  </view>
</template>
<style scoped>
.ultrasonic-config {
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
  margin-bottom: 8rpx;
}

.network-signal,
.network-security {
  font-size: 24rpx;
  color: #65686f;
}

.network-password {
  font-size: 24rpx;
  color: #65686f;
}

.submit-section {
  margin-bottom: 32rpx;
}

.submit-section .wd-button {
  margin-bottom: 16rpx;
}

.submit-section .wd-button:last-child {
  margin-bottom: 0;
}

.audio-options {
  margin-bottom: 32rpx;
  padding: 24rpx;
  background-color: #fbfbfb;
  border-radius: 16rpx;
  border: 1rpx solid #eeeeee;
}

.option-item {
  font-size: 28rpx;
}

.audio-player {
  margin-bottom: 32rpx;
  padding: 24rpx;
  background-color: #f0f6ff;
  border: 1rpx solid #336cff;
  border-radius: 16rpx;
}

.player-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.audio-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #232338;
}

.audio-duration {
  font-size: 24rpx;
  color: #65686f;
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
