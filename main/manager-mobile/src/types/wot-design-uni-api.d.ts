declare module 'wot-design-uni' {
  export type ConfigProviderThemeVars = Record<string, string | number | undefined>

  export function useMessage(): any
  export function useToast(): any
}

export {}
