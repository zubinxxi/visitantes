<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

function getToastClasses(type: string) {
  const base = 'flex items-center gap-3 rounded-lg border px-4 py-3 shadow-theme-xs'
  switch (type) {
    case 'success':
      return `${base} border-success-200 dark:border-success-800 bg-success-50 dark:bg-success-900/20`
    case 'error':
      return `${base} border-error-200 dark:border-error-800 bg-error-50 dark:bg-error-900/20`
    case 'warning':
      return `${base} border-warning-200 dark:border-warning-800 bg-warning-50 dark:bg-warning-900/20`
    case 'info':
      return `${base} border-brand-200 dark:border-brand-800 bg-brand-50 dark:bg-brand-900/20`
    default:
      return `${base} border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900`
  }
}

function getIconColor(type: string) {
  switch (type) {
    case 'success':
      return 'text-success-600 dark:text-success-400'
    case 'error':
      return 'text-error-600 dark:text-error-400'
    case 'warning':
      return 'text-warning-600 dark:text-warning-400'
    case 'info':
      return 'text-brand-600 dark:text-brand-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
}

function getMessageColor(type: string) {
  switch (type) {
    case 'success':
      return 'text-success-700 dark:text-success-300'
    case 'error':
      return 'text-error-700 dark:text-error-300'
    case 'warning':
      return 'text-warning-700 dark:text-warning-300'
    case 'info':
      return 'text-brand-700 dark:text-brand-300'
    default:
      return 'text-gray-700 dark:text-gray-300'
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      <TransitionGroup
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform -translate-x-8 opacity-0"
        enter-to-class="transform translate-x-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-x-0 opacity-100"
        leave-to-class="transform -translate-x-8 opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="getToastClasses(toast.type)"
        >
          <!-- Icon -->
          <svg
            v-if="toast.type === 'success'"
            :class="['w-5 h-5 flex-shrink-0', getIconColor(toast.type)]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg
            v-else-if="toast.type === 'error'"
            :class="['w-5 h-5 flex-shrink-0', getIconColor(toast.type)]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg
            v-else-if="toast.type === 'warning'"
            :class="['w-5 h-5 flex-shrink-0', getIconColor(toast.type)]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <svg
            v-else
            :class="['w-5 h-5 flex-shrink-0', getIconColor(toast.type)]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>

          <!-- Message -->
          <p :class="['text-theme-sm font-medium flex-1', getMessageColor(toast.type)]">
            {{ toast.message }}
          </p>

          <!-- Close button -->
          <button
            @click="remove(toast.id)"
            class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
