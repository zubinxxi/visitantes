import { ref, computed, watch, onMounted } from 'vue'
import { defineStore } from 'pinia'

type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('light')
  const isInitialized = ref(false)

  const isDarkMode = computed(() => theme.value === 'dark')

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
  }

  onMounted(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null
    theme.value = savedTheme || 'light'
    isInitialized.value = true

    if (theme.value === 'dark') {
      document.documentElement.classList.add('dark')
    }
  })

  watch([theme, isInitialized], ([newTheme, newIsInitialized]) => {
    if (newIsInitialized) {
      localStorage.setItem('theme', newTheme)
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  })

  return { theme, isDarkMode, isInitialized, toggleTheme, setTheme }
})
