import type { DefineComponent } from 'vue'

declare module 'vue' {
  export interface GlobalComponents {
    [key: `Wd${string}`]: DefineComponent<Record<string, never>, Record<string, never>, any>
  }
}

export {}
