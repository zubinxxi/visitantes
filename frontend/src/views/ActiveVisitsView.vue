<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/lib/api'
import type { Visit } from '@/types/visit'
import { useToast } from '@/composables/useToast'
import { useBadgePrinter } from '@/composables/useBadgePrinter'
import BadgePrintPreview from '@/components/BadgePrintPreview.vue'

const { success, error: showError } = useToast()
const { selectedVisits, toggleSelectVisit, isVisitSelected, clearSelection } = useBadgePrinter()

const PANAMA_TZ = 'America/Panama'

const activeVisits = ref<Visit[]>([])
const loading = ref(true)
const showPrintPreview = ref(false)

const hasSelection = computed(() => selectedVisits.value.length > 0)

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString('es-PA', { timeZone: PANAMA_TZ, hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, day: '2-digit', month: 'short', year: 'numeric' })
}

function getElapsedTime(checkIn: string) {
  const now = new Date()
  const check = new Date(checkIn)
  const diff = Math.floor((now.getTime() - check.getTime()) / 60000)
  if (diff < 60) return `${diff} min`
  return `${Math.floor(diff / 60)}h ${diff % 60}m`
}

async function loadActive() {
  loading.value = true
  try {
    const response = await api.get('/visits/active')
    activeVisits.value = response.data
  } catch (error) {
    console.error('Error al cargar visitas activas:', error)
  } finally {
    loading.value = false
  }
}

async function handleCheckout(id: number) {
  try {
    await api.post(`/visits/${id}/checkout`)
    activeVisits.value = activeVisits.value.filter((v) => v.id !== id)
    if (isVisitSelected(activeVisits.value.find((v) => v.id === id) as Visit)) {
      toggleSelectVisit(activeVisits.value.find((v) => v.id === id) as Visit)
    }
    success('Check-out realizado exitosamente')
  } catch (err: unknown) {
    let errMsg = 'Error en check-out'
    if (err && typeof err === 'object' && 'response' in err) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      if (detail) errMsg = detail
    } else if (err instanceof Error) {
      errMsg = err.message
    }
    showError(errMsg)
  }
}

function handlePrintSingle(visit: Visit) {
  selectedVisits.value = [visit]
  showPrintPreview.value = true
}

function handlePrintSelected() {
  if (!hasSelection.value) return
  showPrintPreview.value = true
}

function selectAll() {
  if (selectedVisits.value.length === activeVisits.value.length) {
    clearSelection()
  } else {
    selectedVisits.value = [...activeVisits.value]
  }
}

function handlePrintPreviewClose() {
  showPrintPreview.value = false
}

onMounted(loadActive)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Visitas Activas</h1>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ activeVisits.length }} visitantes actualmente en el edificio</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          v-if="hasSelection"
          @click="handlePrintSelected"
          class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Imprimir ({{ selectedVisits.length }})
        </button>
        <button
          @click="loadActive"
          class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
        >
          <svg class="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refrescar
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div
      v-else-if="activeVisits.length === 0"
      class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-medium text-gray-900 dark:text-white">Sin visitantes activos</h3>
      <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">No hay visitas registradas en este momento</p>
    </div>

    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-4 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400 w-10">
                <input
                  type="checkbox"
                  :checked="selectedVisits.length === activeVisits.length && activeVisits.length > 0"
                  @change="selectAll"
                  class="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500/20 cursor-pointer"
                />
              </th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Visitante</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Cédula</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Check-In</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Tiempo</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="visit in activeVisits" :key="visit.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-4 py-4">
                <input
                  type="checkbox"
                  :checked="isVisitSelected(visit)"
                  @change="toggleSelectVisit(visit)"
                  class="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500/20 cursor-pointer"
                />
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-theme-sm">
                    {{ visit.names?.charAt(0) || '?' }}{{ visit.surnames?.charAt(0) || '' }}
                  </div>
                  <div>
                    <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ visit.names }} {{ visit.surnames }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visit.id_card_number }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ formatDate(visit.check_in) }} {{ formatTime(visit.check_in) }}</td>
              <td class="px-6 py-4">
                <span class="inline-flex items-center rounded-full bg-success-50 dark:bg-success-500/10 px-2.5 py-1 text-theme-xs font-medium text-success-700 dark:text-success-400">
                  {{ getElapsedTime(visit.check_in) }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="inline-flex gap-2 justify-end">
                  <button
                    @click="handlePrintSingle(visit)"
                    class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3.5 py-2 text-theme-xs font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
                    title="Imprimir gafete"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                  </button>
                  <button
                    @click="handleCheckout(visit.id)"
                    class="rounded-lg border border-error-200 dark:border-error-800 bg-error-50 dark:bg-error-900/20 px-3.5 py-2 text-theme-xs font-medium text-error-600 dark:text-error-400 shadow-theme-xs hover:bg-error-100 dark:hover:bg-error-900/30"
                  >
                    Check-Out
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <BadgePrintPreview
      v-model="showPrintPreview"
      :visits="selectedVisits"
      close-label="Salir"
      @close="handlePrintPreviewClose"
    />
  </div>
</template>
