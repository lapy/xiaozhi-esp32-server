/// <reference types="vite/client" />
/// <reference types="vite-svg-loader" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  /** Website title, application name */
  readonly VITE_APP_TITLE: string
  /** Service port number */
  readonly VITE_SERVER_PORT: string
  /** Backend API address */
  readonly VITE_SERVER_BASEURL: string
  /** Whether H5 needs proxy */
  readonly VITE_APP_PROXY: 'true' | 'false'
  /** Whether H5 needs proxy, if needed there is a prefix */
  readonly VITE_APP_PROXY_PREFIX: string // Usually /api
  /** Upload image address */
  readonly VITE_UPLOAD_BASEURL: string
  /** Whether to clear console */
  readonly VITE_DELETE_CONSOLE: string
  // More environment variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare const __VITE_APP_PROXY__: 'true' | 'false'
declare const __UNI_PLATFORM__: 'app' | 'h5' | 'mp-alipay' | 'mp-baidu' | 'mp-kuaishou' | 'mp-lark' | 'mp-qq' | 'mp-tiktok' | 'mp-weixin' | 'mp-xiaochengxu'
