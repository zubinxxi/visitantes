<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const PANAMA_TZ = 'America/Panama'

interface Props {
  visitId?: number
  visitorName?: string
  idCardNumber?: string
  checkIn?: string
  uadms?: string
  buildings?: string
  labelWidth?: number
  labelHeight?: number
}

const props = defineProps<Props>()

const qrCodeUrl = ref('')

const badgeWidth = computed(() => props.labelWidth || 397)
const badgeHeight = computed(() => props.labelHeight || 287)

const buildingColumns = ['1', '2', '3', '4', '5', '6', 'P']

function parseBuildingIds(buildingStr: string): number[] {
  if (!buildingStr) {
    return []
  }
  return buildingStr
    .replace(';', ',')
    .split(',')
    .map(b => parseInt(b.trim(), 10))
    .filter(n => !isNaN(n))
}

const buildingIds = computed(() => parseBuildingIds(props.buildings || ''))

function isBuildingSelected(colIndex: number): boolean {
  const targetId = colIndex === 6 ? 7 : colIndex + 1
  return buildingIds.value.includes(targetId)
}

function formatCheckInPanama(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const day = date.toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, day: '2-digit' })
  const month = date.toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, month: 'short' }).toUpperCase()
  const year = date.toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, year: 'numeric' })
  const time = date.toLocaleTimeString('es-PA', {
    timeZone: PANAMA_TZ,
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
  return `${day}-${month}-${year} ${time}`
}

const formattedCheckIn = computed(() => formatCheckInPanama(props.checkIn || ''))

const uadmsList = computed(() => {
  if (!props.uadms) return []
  return props.uadms.split(',').map(u => u.trim()).filter(u => u)
})

async function generateQrCode() {
  if (!props.visitId) return
  try {
    qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(props.visitId.toString())}`
  } catch (e) {
    console.error('Error generating QR:', e)
  }
}

onMounted(() => {
  generateQrCode()
})
</script>

<template>
  <div class="flex justify-center">
    <div
      class="bg-white overflow-hidden"
      :style="{ width: badgeWidth + 'px', height: badgeHeight + 'px' }"
    >
      <div class="h-full flex flex-col">
        <div style="font-size: 28px; line-height: 1; background-color: black; color: white; text-align: center; font-weight: bold; padding: 4px;">
          V I S I T A N T E
        </div>

        <div class="flex-1 p-2 flex flex-col gap-1">
          <div class="text-center">
            <p class="font-bold text-gray-900" style="font-size: 14pt; text-transform: uppercase;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p class="text-gray-900" style="font-size: 10pt;">
              CED: {{ idCardNumber }} | {{ formattedCheckIn }}
            </p>
          </div>

          <div v-if="uadmsList.length > 0">
            <div class="bg-gray-200 border border-black px-1" style="font-size: 7.5pt;">
              UNIDAD ADMINISTRATIVA VISITADA
            </div>
            <div class="border border-t-0 border-black px-1" style="font-size: 7pt;">
              <div v-for="(uadm, idx) in uadmsList" :key="idx">• {{ uadm }}</div>
            </div>
          </div>

          <div>
            <div class="bg-gray-200 border border-black px-1" style="font-size: 7.5pt;">
              EDIFICIOS AUTORIZADOS
            </div>
            <table class="w-full" style="border-collapse: collapse; border: 1px solid black;">
              <thead>
                <tr>
                  <th v-for="(col, idx) in buildingColumns" :key="idx"
                      style="background-color: #e5e7eb; font-size: 8pt; width: 14.28%; border: 1px solid black; text-align: center; font-weight: bold;">
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td v-for="(col, idx) in buildingColumns" :key="idx"
                      :style="[
                        { height: '18px', width: '14.28%' },
                        isBuildingSelected(idx) ? { backgroundColor: 'black', border: '1px solid black' } : { backgroundColor: 'white', border: '1px solid black' }
                      ]">
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex-1 flex items-center justify-between mt-auto">
            <div class="flex items-center">
              <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR" style="width: 16mm; height: 16mm;" />
            </div>
            <div class="flex items-center">
              <img src="/img/logo_negro_blanco.png" alt="AMP" style="width: 25mm; max-height: 12mm;" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  body > * {
    display: none !important;
  }
  
  .visitor-badge-wrapper {
    display: block !important;
  }
  
  .visitor-badge-wrapper * {
    display: block !important;
  }

  .bg-black, [style*="backgroundColor: black"] {
    background-color: black !important;
    color: white !important;
  }

  .bg-gray-200 {
    background-color: #e5e7eb !important;
  }

  td, th {
    border: 1px solid black !important;
  }
}
</style>