<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Visit } from '@/types/visit'
import VisitorBadge from '@/components/VisitorBadge.vue'

interface Props {
  modelValue: boolean
  visits: Visit[]
  labelWidth?: number
  labelHeight?: number
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isLoaded = ref(false)

const defaultLabelWidth = 397
const defaultLabelHeight = 287

const hasVisits = computed(() => props.visits.length > 0)

const visitBuildings = (visit: Visit) => {
  const raw = visit.buildings_visited || ''
  if (raw && /^\d+[,\d]*$/.test(raw)) {
    return raw
  }
  return ''
}

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        isLoaded.value = true
      }, 100)
    } else {
      isLoaded.value = false
    }
  },
)

function handlePrint() {
  window.print()
}

function handleClose() {
  emit('update:modelValue', false)
}

function getVisitorName(visit: Visit): string {
  return `${visit.names} ${visit.surnames}`.trim() || 'N/A'
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4 print-modal"
      >
        <div class="w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl flex flex-col print-container">
          <!-- Header (solo visible en pantalla) -->
          <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4 no-print">
            <div>
              <h3 class="text-base font-medium text-gray-800 dark:text-white">Vista Previa de Gafetes</h3>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                {{ visits.length }} gafete{{ visits.length > 1 ? 's' : '' }} listo{{ visits.length > 1 ? 's' : '' }} para imprimir
              </p>
            </div>
            <div class="flex items-center gap-3">
              <button
                @click="handlePrint"
                class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Imprimir
              </button>
              <button
                @click="handleClose"
                class="rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                Cerrar
              </button>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto p-6 badge-preview-container">
            <div v-if="hasVisits" class="flex flex-wrap gap-6 justify-center print-badges-wrapper">
              <VisitorBadge
                v-for="visit in visits"
                :key="visit.id"
                :visit-id="visit.id"
                :visitor-name="getVisitorName(visit)"
                :id-card-number="visit.id_card_number"
                :check-in="visit.check_in"
                :uadms="visit.uadms_names || ''"
                :buildings="visitBuildings(visit)"
                :label-width="labelWidth || defaultLabelWidth"
                :label-height="labelHeight || defaultLabelHeight"
              />
            </div>
            <div v-else class="flex flex-col items-center justify-center py-16 text-gray-500">
              <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <p class="text-base font-medium">No hay gafetes para mostrar</p>
              <p class="text-theme-sm">Selecciona visitantes para imprimir sus gafetes</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@media print {
  .print-modal {
    position: static !important;
    background: none !important;
    backdrop-filter: none !important;
    padding: 0 !important;
    display: block !important;
  }

  .print-container {
    max-height: none !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
  }

  .no-print {
    display: none !important;
  }

  .badge-preview-container {
    padding: 0 !important;
    overflow: visible !important;
  }

  .print-badges-wrapper {
    gap: 0 !important;
    justify-content: flex-start !important;
    flex-direction: column !important;
    align-items: center !important;
  }
}
</style>
