/**
 * Toast popup component
 * Supports success/error/warning/info four states
 * Configurable duration, position and other parameters
 */

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastOptions {
  type?: ToastType
  duration?: number
  position?: 'top' | 'middle' | 'bottom'
  icon?: 'success' | 'error' | 'none' | 'loading' | 'fail' | 'exception'
  message: string
}

export function showToast(options: ToastOptions | string) {
  const defaultOptions: ToastOptions = {
    type: 'info',
    duration: 2000,
    position: 'middle',
    message: '',
  }
  const mergedOptions
    = typeof options === 'string'
      ? { ...defaultOptions, message: options }
      : { ...defaultOptions, ...options }
  // Map position to uniapp supported format
  const positionMap: Record<ToastOptions['position'], 'top' | 'bottom' | 'center'> = {
    top: 'top',
    middle: 'center',
    bottom: 'bottom',
  }

  // Map icon type
  const iconMap: Record<
    ToastType,
    'success' | 'error' | 'none' | 'loading' | 'fail' | 'exception'
  > = {
    success: 'success',
    error: 'error',
    warning: 'fail',
    info: 'none',
  }

  // Call uni.showToast to display prompt
  uni.showToast({
    title: mergedOptions.message,
    duration: mergedOptions.duration,
    position: positionMap[mergedOptions.position],
    icon: mergedOptions.icon || iconMap[mergedOptions.type],
    mask: true,
  })
}

export const toast = {
  success: (message: string, options?: Omit<ToastOptions, 'type'>) =>
    showToast({ ...options, type: 'success', message }),
  error: (message: string, options?: Omit<ToastOptions, 'type'>) =>
    showToast({ ...options, type: 'error', message }),
  warning: (message: string, options?: Omit<ToastOptions, 'type'>) =>
    showToast({ ...options, type: 'warning', message }),
  info: (message: string, options?: Omit<ToastOptions, 'type'>) =>
    showToast({ ...options, type: 'info', message }),
}
