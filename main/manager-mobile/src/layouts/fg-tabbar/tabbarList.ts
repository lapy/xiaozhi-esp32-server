import type { TabBar } from '@uni-helper/vite-plugin-uni-pages'

type FgTabBarItem = TabBar['list'][0] & {
  icon: string
  iconType: 'uiLib' | 'unocss' | 'iconfont'
}

/**
 * Tabbar selection strategy, see tabbar.md file for more detailed introduction
 * 0: 'NO_TABBAR' `No tabbar`
 * 1: 'NATIVE_TABBAR'  `Fully native tabbar`
 * 2: 'CUSTOM_TABBAR_WITH_CACHE' `Custom tabbar with cache`
 * 3: 'CUSTOM_TABBAR_WITHOUT_CACHE' `Custom tabbar without cache`
 *
 * Friendly reminder: After any code changes in this file, need to restart, otherwise pages.json will not update causing errors
 */
export const TABBAR_MAP = {
  NO_TABBAR: 0,
  NATIVE_TABBAR: 1,
  CUSTOM_TABBAR_WITH_CACHE: 2,
  CUSTOM_TABBAR_WITHOUT_CACHE: 3,
}
// TODO: Switch tabbar strategy here
export const selectedTabbarStrategy = TABBAR_MAP.NATIVE_TABBAR

// When selectedTabbarStrategy==NATIVE_TABBAR(1), need to fill iconPath and selectedIconPath
// When selectedTabbarStrategy==CUSTOM_TABBAR(2,3), need to fill icon and iconType
// When selectedTabbarStrategy==NO_TABBAR(0), tabbarList is not effective
export const tabbarList: FgTabBarItem[] = [
  {
    iconPath: 'static/tabbar/robot.png',
    selectedIconPath: 'static/tabbar/robot_activate.png',
    pagePath: 'pages/index/index',
    text: 'Home',
    icon: 'home',
    // When using UI framework built-in icon, iconType is uiLib
    iconType: 'uiLib',
  },
  {
    iconPath: 'static/tabbar/network.png',
    selectedIconPath: 'static/tabbar/network_activate.png',
    pagePath: 'pages/device-config/index',
    text: 'Network Config',
    icon: 'i-carbon-network-3',
    iconType: 'uiLib',
  },
  {
    iconPath: 'static/tabbar/system.png',
    selectedIconPath: 'static/tabbar/system_activate.png',
    pagePath: 'pages/settings/index',
    text: 'System',
    icon: 'i-carbon-settings',
    iconType: 'uiLib',
  },
]

// When NATIVE_TABBAR(1) and CUSTOM_TABBAR_WITH_CACHE(2), tabbar cache is needed
export const cacheTabbarEnable = selectedTabbarStrategy === TABBAR_MAP.NATIVE_TABBAR
  || selectedTabbarStrategy === TABBAR_MAP.CUSTOM_TABBAR_WITH_CACHE

const _tabbar: TabBar = {
  // Only WeChat Mini Program supports custom. App and H5 are not effective
  custom: selectedTabbarStrategy === TABBAR_MAP.CUSTOM_TABBAR_WITH_CACHE,
  color: '#e6e6e6',
  selectedColor: '#667dea',
  backgroundColor: '#fff',
  borderStyle: 'black',
  height: '50px',
  fontSize: '10px',
  iconWidth: '24px',
  spacing: '3px',
  list: tabbarList as unknown as TabBar['list'],
}

// 0 and 1 need to display various configurations of bottom tabbar to utilize cache
export const tabBar = cacheTabbarEnable ? _tabbar : undefined
