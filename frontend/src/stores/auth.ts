import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { usePermissionsStore } from './permissions'

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
      let errorMessage = 'Credenciales inválidas'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        errorMessage = `Error del servidor (${response.status})`
      }
      throw new Error(errorMessage)
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

    // Guardar permisos y grupos en el store de permisos
    const permissionsStore = usePermissionsStore()
    permissionsStore.setPermissions(
      data.permissions || [],
      data.group_ids || [],
      data.user?.priv_admin || 'N',
    )
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')

    const permissionsStore = usePermissionsStore()
    permissionsStore.clearPermissions()
  }

  async function forgotPassword(loginOrEmail: string) {
    const response = await fetch('/api/v1/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login_or_email: loginOrEmail }),
    })

    if (!response.ok) {
      let errorMessage = 'Error al procesar la solicitud'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        errorMessage = `Error del servidor (${response.status})`
      }
      throw new Error(errorMessage)
    }
    return await response.json()
  }

  async function resetPassword(tokenStr: string, newPassword: string) {
    const response = await fetch('/api/v1/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: tokenStr, new_password: newPassword }),
    })

    if (!response.ok) {
      let errorMessage = 'Error al restablecer la contraseña'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        errorMessage = `Error del servidor (${response.status})`
      }
      throw new Error(errorMessage)
    }
    return await response.json()
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    const response = await fetch('/api/v1/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    })

    if (!response.ok) {
      let errorMessage = 'Error al cambiar la contraseña'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        errorMessage = `Error del servidor (${response.status})`
      }
      throw new Error(errorMessage)
    }
    return await response.json()
  }

  return { 
    token, 
    user, 
    isAuthenticated, 
    login, 
    logout, 
    forgotPassword, 
    resetPassword, 
    changePassword 
  }
})
