/**
 * Tabbar state, add storageSync to ensure correct tabbar page when refreshing browser
 * Use reactive simple state instead of pinia global state
 */
export const tabbarStore = reactive({
  curIdx: uni.getStorageSync('app-tabbar-index') || 0,
  setCurIdx(idx: number) {
    this.curIdx = idx
    uni.setStorageSync('app-tabbar-index', idx)
  },
})
