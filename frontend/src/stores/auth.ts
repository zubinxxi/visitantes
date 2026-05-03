import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface User {
  login: string
  name: string
  email: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  function decodeToken(tokenStr: string): User | null {
    try {
      const parts = tokenStr.split('.')
      if (parts.length !== 3) return null
      const rawPayload = parts[1]
      if (!rawPayload) return null
      const payload = JSON.parse(atob(rawPayload))
      if (!payload) return null
      return {
        login: payload.login || payload.sub || '',
        name: payload.name || payload.sub || 'Usuario',
        email: payload.email || '',
        role: payload.role || 'Usuario',
      }
    } catch {
      return null
    }
  }

  if (token.value) {
    user.value = decodeToken(token.value)
  }

  async function login(loginStr: string, password: string) {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: loginStr, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Credenciales inválidas')
    }

    const data = await response.json()
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)

    if (data.user) {
      user.value = {
        login: data.user.login || '',
        name: data.user.name || 'Usuario',
        email: data.user.email || '',
        role: data.user.role || 'Usuario',
      }
    } else {
      user.value = decodeToken(data.access_token)
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isAuthenticated, login, logout }
})
