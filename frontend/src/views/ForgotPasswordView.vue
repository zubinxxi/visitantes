<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()

const loginOrEmail = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleForgotPassword() {
  loading.value = true
  error.value = ''
  success.value = false
  try {
    await auth.forgotPassword(loginOrEmail.value)
    success.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Error al procesar la solicitud'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative p-6 bg-white dark:bg-gray-900 sm:p-0">
    <div class="relative flex flex-col justify-center w-full h-screen lg:flex-row">
      <div class="flex flex-col flex-1 w-full lg:w-1/2">
        <div class="w-full max-w-md pt-10 mx-auto">
          <div class="flex justify-end">
            <button
              @click="themeStore.toggleTheme"
              class="rounded-lg p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
              :title="themeStore.isDarkMode ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
            >
              <svg v-if="!themeStore.isDarkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </button>
          </div>
        </div>

        <div class="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
          <div class="flex justify-center mb-6">
            <img
              src="/img/amp-logo-small-253x95px.png"
              alt="Autoridad Marítima de Panamá"
              class="h-16 w-auto object-contain"
            />
          </div>

          <div class="mb-5 sm:mb-8 text-center">
            <h1 class="mb-2 font-semibold text-gray-800 dark:text-white text-title-sm">
              Recuperar Contraseña
            </h1>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Ingresa tu usuario o correo electrónico para recibir un enlace de recuperación.
            </p>
          </div>

          <div v-if="success" class="mb-6 rounded-lg border border-success-200 dark:border-success-800 bg-success-50 dark:bg-success-900/20 px-4 py-4 text-center">
            <svg class="w-12 h-12 text-success-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="text-lg font-medium text-success-800 dark:text-success-300 mb-1">¡Correo enviado!</h3>
            <p class="text-sm text-success-600 dark:text-success-400 mb-4">Si el usuario existe, recibirás un enlace para restablecer tu contraseña en unos minutos.</p>
            <router-link to="/login" class="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 underline">Volver al inicio de sesión</router-link>
          </div>

          <div v-else>
            <form @submit.prevent="handleForgotPassword">
              <div v-if="error" class="mb-4 rounded-lg border border-error-200 dark:border-error-800 bg-error-50 dark:bg-error-900/20 px-4 py-3">
                <p class="text-sm text-error-600 dark:text-error-400">{{ error }}</p>
              </div>

              <div class="space-y-5">
                <div>
                  <label
                    for="loginOrEmail"
                    class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
                  >
                    Usuario o Correo<span class="text-error-500">*</span>
                  </label>
                  <input
                    v-model="loginOrEmail"
                    type="text"
                    id="loginOrEmail"
                    placeholder="Ingresa tu usuario o correo"
                    class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                    required
                  />
                </div>

                <div>
                  <button
                    type="submit"
                    :disabled="loading"
                    class="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition rounded-lg bg-brand-500 shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
                  >
                    <span
                      v-if="loading"
                      class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
                    ></span>
                    {{ loading ? 'Enviando...' : 'Enviar Enlace de Recuperación' }}
                  </button>
                </div>

                <div class="text-center mt-4">
                  <router-link
                    to="/login"
                    class="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
                  >
                    Volver al inicio de sesión
                  </router-link>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div
        class="relative hidden items-center w-full h-full lg:w-1/2 bg-brand-950 lg:grid"
      >
        <div class="flex items-center justify-center">
          <div class="absolute inset-0 opacity-10">
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.5" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>

          <div class="flex flex-col items-center max-w-xs z-10">
            <div class="mb-6 flex h-16 w-16 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm">
              <span class="text-3xl font-bold text-white">V</span>
            </div>
            <h2 class="mb-2 text-xl font-semibold text-white">VisitantesDB</h2>
            <p class="text-center text-sm text-gray-400">
              Sistema de Gestión de Visitantes<br />Autoridad Marítima de Panamá
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
