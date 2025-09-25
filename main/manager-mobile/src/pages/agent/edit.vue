<script lang="ts" setup>
import type { AgentDetail, ModelOption, PluginDefinition, RoleTemplate } from '@/api/agent/types'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { getAgentDetail, getModelOptions, getPluginFunctions, getRoleTemplates, getTTSVoices, updateAgent } from '@/api/agent/agent'
import { usePluginStore } from '@/store'
import { toast } from '@/utils/toast'

defineOptions({
  name: 'AgentEdit',
})

const props = withDefaults(defineProps<Props>(), {
  agentId: '',
})

// Component parameters
interface Props {
  agentId?: string
}

const agentId = computed(() => props.agentId)

// Form data
const formData = ref<Partial<AgentDetail>>({
  agentName: '',
  systemPrompt: '',
  summaryMemory: '',
  vadModelId: '',
  asrModelId: '',
  llmModelId: '',
  vllmModelId: '',
  intentModelId: '',
  memModelId: '',
  ttsModelId: '',
  ttsVoiceId: '',
})

// Display name data
const displayNames = ref({
  vad: 'Please select',
  asr: 'Please select',
  llm: 'Please select',
  vllm: 'Please select',
  intent: 'Please select',
  memory: 'Please select',
  tts: 'Please select',
  voiceprint: 'Please select',
})

// Agent template data
const roleTemplates = ref<RoleTemplate[]>([])
const selectedTemplateId = ref('')

// Loading status
const loading = ref(false)
const saving = ref(false)

// Model options data
const modelOptions = ref<{
  [key: string]: ModelOption[]
}>({
  VAD: [],
  ASR: [],
  LLM: [],
  VLLM: [],
  Intent: [],
  Memory: [],
  TTS: [],
})

// Voice options data
const voiceOptions = ref<{ id: string, name: string }[]>([])

// Selector display status
const pickerShow = ref<{
  [key: string]: boolean
}>({
  vad: false,
  asr: false,
  llm: false,
  vllm: false,
  intent: false,
  memory: false,
  tts: false,
  voiceprint: false,
})

const allFunctions = ref<PluginDefinition[]>([])

// Use plugin store
const pluginStore = usePluginStore()

// tabs
const tabList = [
  {
    label: 'Agent Configuration',
    value: 'home',
    icon: '/static/tabbar/robot.png',
    activeIcon: '/static/tabbar/robot_activate.png',
  },
  {
    label: 'Device Management',
    value: 'category',
    icon: '/static/tabbar/device.png',
    activeIcon: '/static/tabbar/device_activate.png',
  },
  {
    label: 'Chat History',
    value: 'settings',
    icon: '/static/tabbar/chat.png',
    activeIcon: '/static/tabbar/chat_activate.png',
  },
  {
    label: 'Voiceprint Management',
    value: 'profile',
    icon: '/static/tabbar/voiceprint.png',
    activeIcon: '/static/tabbar/voiceprint_activate.png',
  },
]

// Load agent details
async function loadAgentDetail() {
  if (!agentId.value)
    return

  try {
    loading.value = true
    const detail = await getAgentDetail(agentId.value)
    formData.value = { ...detail }

    // Update plugin store
    pluginStore.setCurrentAgentId(agentId.value)
    pluginStore.setCurrentFunctions(detail.functions || [])

    // If there is a TTS model, load corresponding voice options
    if (detail.ttsModelId) {
      await loadVoiceOptions(detail.ttsModelId)
    }

    // Wait for model options to load before updating display name
    await nextTick()
    updateDisplayNames()
  }
  catch (error) {
    console.error('Failed to load agent details:', error)
    toast.error('Load failed')
  }
  finally {
    loading.value = false
  }
}

// Get voice display name
function getVoiceDisplayName(ttsVoiceId: string) {
  if (!ttsVoiceId)
    return 'Please select'

  console.log('=== Voice mapping debug ===')
  console.log('Current voice ID:', ttsVoiceId)
  console.log('Current TTS model:', formData.value.ttsModelId)
  console.log('Available voice options:', voiceOptions.value)

  // First try to match ID directly from voice options
  const voice = voiceOptions.value.find(v => v.id === ttsVoiceId)
  if (voice) {
    console.log('Direct match successful:', voice)
    return voice.name
  }

  // If not found, try compatibility mapping
  if (voiceOptions.value.length > 0) {
    console.log('Direct match failed, trying compatibility mapping')

    // Create index mapping: voice1 → 1st voice, voice2 → 2nd voice
    const indexMap = {
      voice1: 0,
      voice2: 1,
      voice3: 2,
      voice4: 3,
      voice5: 4,
    }

    const index = indexMap[ttsVoiceId]
    if (index !== undefined && voiceOptions.value[index]) {
      const mappedVoice = voiceOptions.value[index]
      console.log(`Index mapping: ${ttsVoiceId} → index ${index} → ${mappedVoice.name}`)
      return mappedVoice.name
    }
  }

  console.log('All mapping methods failed, returning original ID:', ttsVoiceId)
  return ttsVoiceId
}

// Update display names
function updateDisplayNames() {
  if (!formData.value)
    return

  displayNames.value.vad = getModelDisplayName('VAD', formData.value.vadModelId)
  displayNames.value.asr = getModelDisplayName('ASR', formData.value.asrModelId)
  displayNames.value.llm = getModelDisplayName('LLM', formData.value.llmModelId)
  displayNames.value.vllm = getModelDisplayName('VLLM', formData.value.vllmModelId)
  displayNames.value.intent = getModelDisplayName('Intent', formData.value.intentModelId)
  displayNames.value.memory = getModelDisplayName('Memory', formData.value.memModelId)
  displayNames.value.tts = getModelDisplayName('TTS', formData.value.ttsModelId)

  // Special handling for character voice
  displayNames.value.voiceprint = getVoiceDisplayName(formData.value.ttsVoiceId || '')

  console.log('Final voice display name:', displayNames.value.voiceprint)
}

// Load role templates
async function loadRoleTemplates() {
  try {
    const templates = await getRoleTemplates()
    roleTemplates.value = templates
  }
  catch (error) {
    console.error('Failed to load role templates:', error)
  }
}

// Load model options
async function loadModelOptions() {
  const modelTypes = ['VAD', 'ASR', 'LLM', 'VLLM', 'Intent', 'Memory', 'TTS']

  try {
    await Promise.all(
      modelTypes?.map(async (type) => {
        console.log(`Loading model type: ${type}`)
        const options = await getModelOptions(type)
        modelOptions.value[type] = options
        console.log(`${type} options:`, options)
      }) || [],
    )
    console.log('All model options loaded:', modelOptions.value)
  }
  catch (error) {
    console.error('Failed to load model options:', error)
  }
}

// Load TTS voice options
async function loadVoiceOptions(ttsModelId?: string) {
  if (!ttsModelId)
    return

  try {
    console.log(`Loading voice options: ${ttsModelId}`)
    const voices = await getTTSVoices(ttsModelId)
    voiceOptions.value = voices
    console.log('Voice options:', voices)
  }
  catch (error) {
    console.error('Failed to load voice options:', error)
    voiceOptions.value = []
  }
}

// Select role template
function selectRoleTemplate(templateId: string) {
  if (selectedTemplateId.value === templateId) {
    selectedTemplateId.value = ''
    return
  }

  selectedTemplateId.value = templateId
  const template = roleTemplates.value.find(t => t.id === templateId)
  if (template) {
    formData.value.systemPrompt = template.systemPrompt
    formData.value.vadModelId = template.vadModelId
    formData.value.asrModelId = template.asrModelId
    formData.value.llmModelId = template.llmModelId
    formData.value.vllmModelId = template.vllmModelId
    formData.value.intentModelId = template.intentModelId
    formData.value.memModelId = template.memModelId
    formData.value.ttsModelId = template.ttsModelId
    formData.value.ttsVoiceId = template.ttsVoiceId
  }
}

// Open picker
function openPicker(type: string) {
  pickerShow.value[type] = true
}

// Picker confirmation
async function onPickerConfirm(type: string, value: any, name: string) {
  console.log('Picker confirmation:', type, value, name)

  // Save display name
  displayNames.value[type] = name

  switch (type) {
    case 'vad':
      formData.value.vadModelId = value
      break
    case 'asr':
      formData.value.asrModelId = value
      break
    case 'llm':
      formData.value.llmModelId = value
      break
    case 'vllm':
      formData.value.vllmModelId = value
      break
    case 'intent':
      formData.value.intentModelId = value
      displayNames.value.intent = name // Ensure display name is updated correctly
      break
    case 'memory':
      formData.value.memModelId = value
      displayNames.value.memory = name // Ensure display name is updated correctly
      break
    case 'tts':
      formData.value.ttsModelId = value
      // When selecting TTS model, automatically load corresponding voice options
      await loadVoiceOptions(value)
      // Reset voice selection
      formData.value.ttsVoiceId = ''
      displayNames.value.voiceprint = 'Please select'
      break
    case 'voiceprint':
      formData.value.ttsVoiceId = value
      displayNames.value.voiceprint = name // Ensure display name is updated correctly
      break
  }

  pickerShow.value[type] = false
}

// Picker cancel
function onPickerCancel(type: string) {
  pickerShow.value[type] = false
}

// Get model display name
function getModelDisplayName(modelType: string, modelId: string) {
  if (!modelId)
    return 'Please select'

  // Find matching ID directly from API configuration data
  const options = modelOptions.value[modelType]

  if (!options || options.length === 0) {
    return modelId
  }

  const option = options.find(opt => opt.id === modelId)
  if (option) {
    return option.modelName
  }
  return modelId
}

// Save agent
async function saveAgent() {
  if (!formData.value.agentName?.trim()) {
    toast.warning('Please enter assistant nickname')
    return
  }

  if (!formData.value.systemPrompt?.trim()) {
    toast.warning('Please enter role introduction')
    return
  }

  try {
    saving.value = true
    await updateAgent(agentId.value, formData.value)

    toast.success('Saved successfully')
  }
  catch (error) {
    console.error('Save failed:', error)
    toast.error('Save failed')
  }
  finally {
    saving.value = false
  }
}

function loadPluginFunctions() {
  getPluginFunctions().then((res) => {
    const processedFunctions = res?.map((item) => {
      const meta = JSON.parse(item.fields || '[]')
      const params = meta.reduce((m: any, f: any) => {
        m[f.key] = f.default
        return m
      }, {})
      return { ...item, fieldsMeta: meta, params }
    }) || []

    allFunctions.value = processedFunctions
    // Also update to store
    pluginStore.setAllFunctions(processedFunctions)
  })
}

function handleTools() {
  console.log('Current plugin configuration:', formData.value.functions)

  // Ensure store has latest data
  pluginStore.setCurrentAgentId(agentId.value)
  pluginStore.setCurrentFunctions(formData.value.functions || [])
  pluginStore.setAllFunctions(allFunctions.value)

  uni.navigateTo({
    url: '/pages/agent/tools',
  })
}

// Listen for plugin configuration updates
function watchPluginUpdates() {
  // Listen for plugin configuration changes in store
  watch(() => pluginStore.currentFunctions, (newFunctions) => {
    console.log('Plugin configuration updated:', newFunctions)
    formData.value.functions = newFunctions
  }, { deep: true })
}

onMounted(async () => {
  // Initialize plugin configuration listener
  watchPluginUpdates()

  // First load model options and role templates
  await Promise.all([
    loadRoleTemplates(),
    loadModelOptions(),
    loadPluginFunctions(),
  ])

  // Then load agent details, so display names can be mapped correctly
  if (agentId.value) {
    await loadAgentDetail()
  }
})
</script>

<template>
  <view class="bg-[#f5f7fb] px-[20rpx]">
    <!-- Basic information title -->
    <view class="pb-[20rpx] first:pt-[20rpx]">
      <text class="text-[32rpx] text-[#232338] font-bold">
        Basic Information
      </text>
    </view>

    <!-- Basic information card -->
    <view class="mb-[24rpx] border border-[#eeeeee] rounded-[20rpx] bg-[#fbfbfb] p-[24rpx]" style="box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);">
      <view class="mb-[24rpx] last:mb-0">
        <text class="mb-[12rpx] block text-[28rpx] text-[#232338] font-medium">
          Assistant Nickname
        </text>
        <input
          v-model="formData.agentName"
          class="box-border h-[80rpx] w-full border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[16rpx_20rpx] text-[28rpx] text-[#232338] leading-[1.4] outline-none focus:border-[#336cff] focus:bg-white placeholder:text-[#9d9ea3]"
          type="text"
          placeholder="Please enter assistant nickname"
        >
      </view>

      <view class="mb-[24rpx] last:mb-0">
        <text class="mb-[12rpx] block text-[28rpx] text-[#232338] font-medium">
          Role Mode
        </text>
        <view class="mt-0 flex flex-wrap gap-[12rpx]">
          <view
            v-for="template in roleTemplates"
            :key="template.id"
            class="cursor-pointer rounded-[20rpx] px-[24rpx] py-[12rpx] text-[24rpx] transition-all duration-300"
            :class="selectedTemplateId === template.id
              ? 'bg-[#336cff] text-white border border-[#336cff]'
              : 'bg-[rgba(51,108,255,0.1)] text-[#336cff] border border-[rgba(51,108,255,0.2)]'"
            @click="selectRoleTemplate(template.id)"
          >
            {{ template.agentName }}
          </view>
        </view>
      </view>

      <view class="mb-[24rpx] last:mb-0">
        <text class="mb-[12rpx] block text-[28rpx] text-[#232338] font-medium">
          Role Description
        </text>
        <textarea
          v-model="formData.systemPrompt"
          :maxlength="2000"
          placeholder="Please enter role description"
          class="box-border h-[500rpx] w-full resize-none break-words break-all border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] text-[26rpx] text-[#232338] leading-[1.6] outline-none focus:border-[#336cff] focus:bg-white placeholder:text-[#9d9ea3]"
        />
        <view class="mt-[8rpx] text-right text-[22rpx] text-[#9d9ea3]">
          {{ (formData.systemPrompt || '').length }}/2000
        </view>
      </view>
    </view>

    <!-- Model configuration title -->
    <view class="pb-[20rpx]">
      <text class="text-[32rpx] text-[#232338] font-bold">
        Model Configuration
      </text>
    </view>

    <!-- Model configuration card -->
    <view class="mb-[24rpx] border border-[#eeeeee] rounded-[20rpx] bg-[#fbfbfb] p-[24rpx]" style="box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);">
      <view class="flex flex-col gap-[16rpx]">
        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('vad')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Voice Activity Detection
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.vad }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('asr')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Speech Recognition
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.asr }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('llm')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Large Language Model
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.llm }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('vllm')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Vision LLM
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.vllm }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('intent')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Intent Recognition
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.intent }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('memory')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Memory
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.memory }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>
      </view>
    </view>

    <!-- Voice Settings Title -->
    <view class="pb-[20rpx]">
      <text class="text-[32rpx] text-[#232338] font-bold">
        Voice Settings
      </text>
    </view>

    <!-- Voice Settings Card -->
    <view class="mb-[24rpx] border border-[#eeeeee] rounded-[20rpx] bg-[#fbfbfb] p-[24rpx]" style="box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);">
      <view class="flex flex-col gap-[16rpx]">
        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('tts')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Speech Synthesis
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.tts }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex cursor-pointer items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx] transition-all duration-300 active:bg-[#eef3ff]" @click="openPicker('voiceprint')">
          <text class="text-[28rpx] text-[#232338] font-medium">
            Character Voice
          </text>
          <text class="mx-[16rpx] flex-1 text-right text-[26rpx] text-[#65686f]">
            {{ displayNames.voiceprint }}
          </text>
          <wd-icon name="arrow-right" custom-class="text-[20rpx] text-[#9d9ea3]" />
        </view>

        <view class="flex items-center justify-between border border-[#eeeeee] rounded-[12rpx] bg-[#f5f7fb] p-[20rpx]">
          <view class="text-[28rpx] text-[#232338] font-medium">
            Plugins
          </view>
          <view class="cursor-pointer rounded-[20rpx] bg-[rgba(51,108,255,0.1)] px-[24rpx] py-[12rpx] text-[24rpx] text-[#336cff] transition-all duration-300 active:bg-[#336cff] active:text-white" @click="handleTools">
            <text>Edit Functions</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Memory History Title -->
    <view class="pb-[20rpx]">
      <text class="text-[32rpx] text-[#232338] font-bold">
        Memory History
      </text>
    </view>

    <!-- Memory History Card -->
    <view class="mb-[24rpx] border border-[#eeeeee] rounded-[20rpx] bg-[#fbfbfb] p-[24rpx]" style="box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);">
      <view class="mb-[24rpx] last:mb-0">
        <textarea
          v-model="formData.summaryMemory"
          placeholder="Memory content"
          disabled
          class="box-border h-[500rpx] w-full resize-none break-words break-all border border-[#eeeeee] rounded-[12rpx] bg-[#f0f0f0] p-[20rpx] text-[26rpx] text-[#65686f] leading-[1.6] opacity-80 outline-none"
        />
      </view>
    </view>

    <!-- Save Button -->
    <view class="mt-[40rpx] p-0">
      <wd-button
        type="primary"
        :loading="saving"
        :disabled="saving"
        custom-class="w-full h-[80rpx] rounded-[16rpx] text-[30rpx] font-semibold bg-[#336cff] active:bg-[#2d5bd1]"
        @click="saveAgent"
      >
        {{ saving ? 'Saving...' : 'Save' }}
      </wd-button>
    </view>
    <!-- Model Selector -->
    <wd-action-sheet
      v-model="pickerShow.vad"
      :actions="modelOptions.VAD && modelOptions.VAD.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('vad')"
      @select="({ item }) => onPickerConfirm('vad', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.asr"
      :actions="modelOptions.ASR && modelOptions.ASR.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('asr')"
      @select="({ item }) => onPickerConfirm('asr', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.llm"
      :actions="modelOptions.LLM && modelOptions.LLM.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('llm')"
      @select="({ item }) => onPickerConfirm('llm', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.vllm"
      :actions="modelOptions.VLLM && modelOptions.VLLM.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('vllm')"
      @select="({ item }) => onPickerConfirm('vllm', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.intent"
      :actions="modelOptions.Intent && modelOptions.Intent.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('intent')"
      @select="({ item }) => onPickerConfirm('intent', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.memory"
      :actions="modelOptions.Memory && modelOptions.Memory.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('memory')"
      @select="({ item }) => onPickerConfirm('memory', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.tts"
      :actions="modelOptions.TTS && modelOptions.TTS.map(item => ({ name: item.modelName, value: item.id }))"
      @close="onPickerCancel('tts')"
      @select="({ item }) => onPickerConfirm('tts', item.value, item.name)"
    />

    <wd-action-sheet
      v-model="pickerShow.voiceprint"
      :actions="voiceOptions && voiceOptions.map(item => ({ name: item.name, value: item.id }))"
      @close="onPickerCancel('voiceprint')"
      @select="({ item }) => onPickerConfirm('voiceprint', item.value, item.name)"
    />
  </view>
</template>
