<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/lib/api'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { success, error: showError } = useToast()

const qrInputRef = ref<HTMLInputElement | null>(null)
const qrInput = ref('')
const scanning = ref(false)
const processingQr = ref(false)
const visitorName = ref('')
const checkOutTime = ref('')

const PANAMA_TZ = 'America/Panama'

function focusQrInput() {
  nextTick(() => qrInputRef.value?.focus())
}

onMounted(focusQrInput)

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString('es-PA', { timeZone: PANAMA_TZ, hour: '2-digit', minute: '2-digit' })
}

async function handleQrInput(event: Event) {
  if (processingQr.value) return
  
  const value = (event.target as HTMLInputElement).value
  if (!value) return
  
  if (event instanceof KeyboardEvent && (event as KeyboardEvent).key !== 'Enter') {
    return
  }
  
  processingQr.value = true
  qrInput.value = value
  try {
    await processQr(value)
  } finally {
    qrInput.value = ''
    processingQr.value = false
  }
}

async function processQr(rawData: string) {
  try {
    scanning.value = true
    const response = await api.post('/visits/checkout-by-qr', { visit_id: rawData })
    const data = response.data
    
    visitorName.value = `${data.visitor_names} ${data.visitor_surnames}`
    checkOutTime.value = formatTime(data.check_out)

    success(`Checkout exitoso: ${visitorName.value}`)
    
    setTimeout(() => {
      router.push('/')
    }, 3000)
  } catch (err: unknown) {
    let errMsg = 'Error al procesar checkout'
    if (err && typeof err === 'object' && 'response' in err) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      if (detail) errMsg = detail
    } else if (err instanceof Error) {
      errMsg = err.message
    }
    showError(errMsg)
  } finally {
    scanning.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-medium text-gray-800 dark:text-white">Checkout Rápido</h1>
      <p class="text-theme-sm text-gray-500 dark:text-gray-400">Escanee el QR de la cédula para registrar la salida</p>
    </div>

    <div class="max-w-md mx-auto">
      <div v-if="visitorName" class="mb-6 rounded-xl border border-success-200 dark:border-success-800 bg-success-50 dark:bg-success-900/20 p-6 text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success-100 dark:bg-success-800/30 text-success-600 dark:text-success-400 mb-4">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">Salida Registrada</h3>
        <p class="text-theme-sm text-gray-600 dark:text-gray-300">{{ visitorName }}</p>
        <p class="text-theme-xs text-gray-500 dark:text-gray-400 mt-1">Salida: {{ checkOutTime }}</p>
      </div>

      <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6">
        <h3 class="text-base font-medium text-gray-800 dark:text-white mb-4">Escanear QR</h3>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400 mb-4">
          Utilice el lector de código de barras/QR para escanear el código de la etiqueta del visitante
        </p>
        <input
          v-model="qrInput"
          @keydown.enter="handleQrInput"
          @blur="handleQrInput"
          type="text"
          class="h-14 w-full text-lg rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
          placeholder="Escanee la cédula aquí..."
          ref="qrInputRef"
        />
        <div v-if="scanning" class="mt-4 flex items-center justify-center">
          <span class="h-6 w-6 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
          <span class="ml-2 text-gray-600 dark:text-gray-400">Procesando...</span>
        </div>
      </div>

      <div class="mt-6 text-center">
        <button
          @click="router.push('/')"
          class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
        >
          Volver al Dashboard
        </button>
      </div>
    </div>
  </div>
</template>
