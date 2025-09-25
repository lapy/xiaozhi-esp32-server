// Agent list data type
export interface Agent {
  id: string
  agentName: string
  ttsModelName: string
  ttsVoiceName: string
  llmModelName: string
  vllmModelName: string
  memModelId: string
  systemPrompt: string
  summaryMemory: string | null
  lastConnectedAt: string | null
  deviceCount: number
}

// Agent creation data type
export interface AgentCreateData {
  agentName: string
}

// Agent details data type
export interface AgentDetail {
  id: string
  userId: string
  agentCode: string
  agentName: string
  asrModelId: string
  vadModelId: string
  llmModelId: string
  vllmModelId: string
  ttsModelId: string
  ttsVoiceId: string
  memModelId: string
  intentModelId: string
  chatHistoryConf: number
  systemPrompt: string
  summaryMemory: string
  langCode: string
  language: string
  sort: number
  creator: string
  createdAt: string
  updater: string
  updatedAt: string
  functions: AgentFunction[]
}

export interface AgentFunction {
  id?: string
  agentId?: string
  pluginId: string
  paramInfo: Record<string, string | number | boolean> | null
}

// Role template data type
export interface RoleTemplate {
  id: string
  agentCode: string
  agentName: string
  asrModelId: string
  vadModelId: string
  llmModelId: string
  vllmModelId: string
  ttsModelId: string
  ttsVoiceId: string
  memModelId: string
  intentModelId: string
  chatHistoryConf: number
  systemPrompt: string
  summaryMemory: string
  langCode: string
  language: string
  sort: number
  creator: string
  createdAt: string
  updater: string
  updatedAt: string
}

// Model options data type
export interface ModelOption {
  id: string
  modelName: string
}

export interface PluginField {
  key: string
  type: string
  label: string
  default: string
  selected?: boolean
  editing?: boolean
}

export interface PluginDefinition {
  id: string
  modelType: string
  providerCode: string
  name: string
  fields: PluginField[] // Note: Original is string, need to JSON.parse first
  sort: number
  updater: string
  updateDate: string
  creator: string
  createDate: string
  [key: string]: any
}
