import type { AgentFunction, PluginDefinition } from '@/api/agent/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePluginStore = defineStore(
  'plugin',
  () => {
    // All available plugins
    const allFunctions = ref<PluginDefinition[]>([])

    // Current agent plugin configuration
    const currentFunctions = ref<AgentFunction[]>([])

    // Currently editing agent ID
    const currentAgentId = ref('')

    // Set all available plugins
    const setAllFunctions = (functions: PluginDefinition[]) => {
      allFunctions.value = functions
    }

    // Set current agent plugin configuration
    const setCurrentFunctions = (functions: AgentFunction[]) => {
      currentFunctions.value = functions
    }

    // Set current agent ID
    const setCurrentAgentId = (agentId: string) => {
      currentAgentId.value = agentId
    }

    // Update plugin configuration (called when saving)
    const updateFunctions = (functions: AgentFunction[]) => {
      currentFunctions.value = functions
    }

    // Clear data
    const clear = () => {
      allFunctions.value = []
      currentFunctions.value = []
      currentAgentId.value = ''
    }

    return {
      allFunctions,
      currentFunctions,
      currentAgentId,
      setAllFunctions,
      setCurrentFunctions,
      setCurrentAgentId,
      updateFunctions,
      clear,
    }
  },
  {
    persist: false, // Not persistent, reload every time entering page
  },
)
