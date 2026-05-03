import { ref } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

const toasts = ref<Toast[]>([])
let nextId = 0

export function useToast() {
  function add(message: string, type: Toast['type'] = 'info', duration = 4000) {
    const id = nextId++
    const toast: Toast = { id, message, type }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }

    return id
  }

  function remove(id: number) {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  function success(message: string, duration?: number) {
    return add(message, 'success', duration)
  }

  function error(message: string, duration?: number) {
    return add(message, 'error', duration)
  }

  function warning(message: string, duration?: number) {
    return add(message, 'warning', duration)
  }

  function info(message: string, duration?: number) {
    return add(message, 'info', duration)
  }

  return {
    toasts,
    add,
    remove,
    success,
    error,
    warning,
    info,
  }
}
