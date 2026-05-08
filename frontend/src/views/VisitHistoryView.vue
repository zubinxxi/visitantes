<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/lib/api'
import type { Visit } from '@/types/visit'
import Modal from '@/components/Modal.vue'
import Multiselect from 'vue-multiselect'

const PANAMA_TZ = 'America/Panama'

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Activas' },
  { value: 'completed', label: 'Finalizadas' },
]

const visits = ref<Visit[]>([])
const loading = ref(true)
const searched = ref(false)

const currentPage = ref(1)
const totalPages = ref(1)
const totalVisits = ref(0)
const pageSize = 10

const searchQuery = ref('')
const filterStatus = ref<{ value: string; label: string }>(statusOptions[0]!)
const filterDate = ref('')

const selectedVisit = ref<Visit | null>(null)
const showDetailsModal = ref(false)

async function loadVisits() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      limit: pageSize,
    }
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (filterStatus.value.value === 'active') {
      params.active_filter = 'true'
    } else if (filterStatus.value.value === 'completed') {
      params.active_filter = 'false'
    }
    if (filterDate.value) {
      params.date = filterDate.value
    }
    
    const response = await api.get('/visits/paginated', { params })
    visits.value = response.data.items
    totalVisits.value = response.data.total
    totalPages.value = response.data.total_pages
    searched.value = true
  } catch (e) {
    console.error('Error loading visits:', e)
  } finally {
    loading.value = false
  }
}

function formatDateTime(dateStr: string) {
  const date = new Date(dateStr)
  return {
    date: date.toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, day: '2-digit', month: 'short', year: 'numeric' }),
    time: date.toLocaleTimeString('es-PA', { timeZone: PANAMA_TZ, hour: '2-digit', minute: '2-digit' }),
  }
}

function getStatusBadge(visit: Visit) {
  if (visit.check_out) {
    return {
      class: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
      label: 'Finalizada',
    }
  }
  return {
    class: 'bg-success-50 dark:bg-success-500/10 text-success-700 dark:text-success-400',
    label: 'Activa',
  }
}

function viewDetails(visit: Visit) {
  selectedVisit.value = visit
  showDetailsModal.value = true
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadVisits()
  }
}

watch([filterStatus, filterDate], () => {
  currentPage.value = 1
  loadVisits()
})

onMounted(loadVisits)
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-medium text-gray-800 dark:text-white">Historial de Visitas</h1>
      <p class="text-theme-sm text-gray-500 dark:text-gray-400">Consulta y filtra todas las visitas registradas</p>
    </div>

    <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6 mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Buscar
          </label>
          <input
            v-model="searchQuery"
            @keyup.enter="loadVisits"
            type="text"
            placeholder="Nombre o cédula"
            class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
          />
        </div>

        <div class="flex-1">
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Estado
          </label>
          <Multiselect
            v-model="filterStatus"
            :options="statusOptions"
            :searchable="false"
            :close-on-select="true"
            placeholder="Seleccione..."
            label="label"
            track-by="value"
            class="multiselect-dark"
          />
        </div>

        <div class="flex-1">
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Fecha
          </label>
          <input
            v-model="filterDate"
            type="date"
            class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
          />
        </div>

        <div class="flex items-end">
          <button
            @click="loadVisits"
            :disabled="loading"
            class="h-11 rounded-lg bg-brand-500 px-6 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
          >
            Filtrar
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div
      v-else-if="searched && visits.length === 0"
      class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-medium text-gray-900 dark:text-white">Sin resultados</h3>
      <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">No se encontraron visitas con los filtros aplicados</p>
    </div>

    <div v-else-if="visits.length > 0" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Visitante</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Cédula</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Fecha</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Check-In</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Check-Out</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Estado</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400">Acción</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="visit in visits" :key="visit.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-9 w-9 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-theme-sm">
                    {{ visit.names?.charAt(0) || '?' }}{{ visit.surnames?.charAt(0) || '' }}
                  </div>
                  <div>
                    <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ visit.names }} {{ visit.surnames }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visit.id_card_number }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ formatDateTime(visit.check_in).date }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ formatDateTime(visit.check_in).time }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">
                {{ visit.check_out ? formatDateTime(visit.check_out).time : '—' }}
              </td>
              <td class="px-6 py-4">
                <span :class="['inline-flex items-center rounded-full px-2.5 py-1 text-theme-xs font-medium', getStatusBadge(visit).class]">
                  {{ getStatusBadge(visit).label }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <button
                  @click="viewDetails(visit)"
                  class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3.5 py-2 text-theme-xs font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
                >
                  Ver
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex items-center justify-between border-t border-gray-200 dark:border-gray-800 px-6 py-4">
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">
          Mostrando {{ visits.length }} de {{ totalVisits }} visitas
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-1.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            Anterior
          </button>
          <span class="px-3 text-theme-sm text-gray-700 dark:text-gray-200">
            Página {{ currentPage }} de {{ totalPages }}
          </span>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-1.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>

    <Modal v-model="showDetailsModal" title="Detalles de la Visita" size="lg">
      <template v-if="selectedVisit">
        <div class="space-y-4">
          <div class="flex items-center gap-4">
            <div class="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-bold text-xl">
              {{ selectedVisit.names?.charAt(0) || '?' }}{{ selectedVisit.surnames?.charAt(0) || '' }}
            </div>
            <div>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedVisit.names }} {{ selectedVisit.surnames }}</p>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ selectedVisit.id_card_number }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Check-In</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">
                {{ formatDateTime(selectedVisit.check_in).date }} {{ formatDateTime(selectedVisit.check_in).time }}
              </p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Check-Out</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">
                {{ selectedVisit.check_out ? formatDateTime(selectedVisit.check_out).time : 'Aún activo' }}
              </p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Propósito</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisit.purpose || 'No especificado' }}</p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Empresa</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisit.company_represents || 'No especificado' }}</p>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <button
          @click="showDetailsModal = false"
          class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
        >
          Cerrar
        </button>
      </template>
    </Modal>
  </div>
</template>
