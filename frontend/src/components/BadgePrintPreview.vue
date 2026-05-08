<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Visit } from '@/types/visit'
import VisitorBadge from '@/components/VisitorBadge.vue'
import { LABEL_SIZES, type LabelSize } from '@/types/labelSize'

interface Props {
  modelValue: boolean
  visits: Visit[]
  closeLabel?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  closeLabel: 'Cerrar',
})

const emit = defineEmits<Emits>()

const isLoaded = ref(false)
const selectedLabelSize = ref<LabelSize>({ ...LABEL_SIZES[0] } as LabelSize)

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
  const size = selectedLabelSize.value
  const width = size.width
  const height = size.height

  const badgesContainer = document.querySelector('.print-badges-wrapper')
  if (!badgesContainer) return

  const badgesHTML = badgesContainer.innerHTML

  const printCSS = `
    @page { size: ${width}mm ${height}mm; margin: 0; }
    * { box-sizing: border-box; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    html { height: auto; margin: 0; padding: 0; }
    body {
      margin: 0; padding: 0; height: auto; min-height: 0; overflow: hidden;
      font-family: 'Arial', sans-serif;
    }
    .print-badges-wrapper { display: flex; flex-direction: column; gap: 0; }
    .visitor-badge {
      page-break-after: avoid; break-inside: avoid;
      overflow: hidden;
    }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #000; padding: 4px; }
    .bg-black, [style*="background-color: rgb(0, 0, 0)"], [style*="backgroundColor: black"] { background-color: #000 !important; color: #fff !important; }
    .bg-white { background-color: #fff !important; }
    .bg-gray-200 { background-color: #e5e7eb !important; }
    .bg-gray-100 { background-color: #f5f5f5 !important; }
    .flex { display: flex; }
    .flex-row { flex-direction: row; }
    .flex-col { flex-direction: column; }
    .flex-1 { flex: 1 1 0%; }
    .h-full { height: 100%; }
    .items-center { align-items: center; }
    .justify-center { justify-content: center; }
    .justify-between { justify-content: space-between; }
    .gap-0\\.5 { gap: 2px; }
    .gap-1 { gap: 4px; }
    .mt-auto { margin-top: auto; }
    .mt-1\\.5 { margin-top: 6px; }
    .w-full { width: 100%; }
    .p-1\\.5 { padding: 6px; }
    .p-2 { padding: 8px; }
    .p-3 { padding: 12px; }
    .px-1 { padding-left: 4px; padding-right: 4px; }
    .text-center { text-align: center; }
    .text-xs { font-size: 10px; }
    .text-sm { font-size: 12px; }
    .text-lg { font-size: 16px; }
    .text-gray-900 { color: #111827; }
    .font-bold { font-weight: bold; }
    .uppercase { text-transform: uppercase; }
    div[class*="rounded"] { border-radius: 0; }
    .overflow-hidden { overflow: hidden; }
  `

  const printHTML = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gafetes de Visitantes</title>
  <style>${printCSS}</style>
</head>
<body>${badgesHTML}</body>
</html>`

  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  printWindow.document.write(printHTML)
  printWindow.document.close()

  printWindow.onload = () => {
    printWindow.focus()
    printWindow.print()
    printWindow.close()
  }
}

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
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
          <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4 no-print">
            <div>
              <h3 class="text-base font-medium text-gray-800 dark:text-white">Vista Previa de Gafetes</h3>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">
                {{ visits.length }} gafete{{ visits.length > 1 ? 's' : '' }} listo{{ visits.length > 1 ? 's' : '' }} para imprimir
              </p>
            </div>
            <div class="flex items-center gap-3">
              <select
                v-model="selectedLabelSize"
                class="h-10 rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-3 py-2 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs cursor-pointer"
              >
                <option v-for="size in LABEL_SIZES" :key="size.value" :value="size">
                  {{ size.label }}
                </option>
              </select>
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
                {{ closeLabel }}
              </button>
            </div>
          </div>

          <div class="flex-1 overflow-y-auto p-6 badge-preview-container">
            <div class="print-badges-wrapper flex flex-col items-center gap-4">
              <div v-for="visit in visits" :key="visit.id" class="visitor-badge">
                <VisitorBadge
                  :visit-id="visit.id"
                  :visitor-name="getVisitorName(visit)"
                  :id-card-number="visit.id_card_number"
                  :check-in="visit.check_in"
                  :uadms="visit.uadms_names || ''"
                  :buildings="visitBuildings(visit)"
                  :label-type="selectedLabelSize.value"
                />
              </div>
              <div v-if="!hasVisits" class="flex flex-col items-center justify-center py-16 text-gray-500">
                <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                <p class="text-base font-medium">No hay gafetes para mostrar</p>
                <p class="text-theme-sm">Selecciona visitantes para imprimir sus gafetes</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
}
</style>