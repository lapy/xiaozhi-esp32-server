<script setup lang="ts">
import { onHide, onLaunch, onShow } from '@dcloudio/uni-app'
import { usePageAuth } from '@/hooks/usePageAuth'
import { useConfigStore } from '@/store'
import 'abortcontroller-polyfill/dist/abortcontroller-polyfill-only'

usePageAuth()

const configStore = useConfigStore()

onLaunch(() => {
  console.log('App Launch')
  // Get public config
  configStore.fetchPublicConfig().catch((error) => {
    console.error('Failed to get public config:', error)
  })
})
onShow(() => {
  console.log('App Show')
})
onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
swiper,
scroll-view {
  flex: 1;
  height: 100%;
  overflow: hidden;
}

image {
  width: 100%;
  height: 100%;
  vertical-align: middle;
}
</style>
