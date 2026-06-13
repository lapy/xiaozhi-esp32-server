import { defineStore } from 'pinia'

export interface ContextProvider {
  url: string
  headers: Record<string, string>
}

export const useProvider = defineStore('provider', () => {
  const providers = ref<ContextProvider[]>([])

  const updateProviders = (val: ContextProvider[]) => {
    providers.value = val
  }

  return {
    providers,
    updateProviders,
  }
}, {
  persist: {
    key: 'providers',
    serializer: {
      serialize: state => JSON.stringify(state.providers),
      deserialize: value => ({ providers: JSON.parse(value) }),
    },
  },
})
