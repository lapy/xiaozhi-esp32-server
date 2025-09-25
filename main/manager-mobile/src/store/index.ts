import { createPinia } from 'pinia'
import { createPersistedState } from 'pinia-plugin-persistedstate' // Data persistence

const store = createPinia()
store.use(
  createPersistedState({
    storage: {
      getItem: uni.getStorageSync,
      setItem: uni.setStorageSync,
    },
  }),
)

export default store

export * from './config'
export * from './plugin'
// Module unified export
export * from './user'
