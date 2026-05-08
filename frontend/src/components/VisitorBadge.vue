<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import QRCode from 'qrcode'

const PANAMA_TZ = 'America/Panama'

interface Props {
  visitId?: number
  visitorName?: string
  idCardNumber?: string
  checkIn?: string
  buildings?: string
  uadms?: string
  labelWidth?: number
  labelHeight?: number
  labelType?: string
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: 101.6,
  labelHeight: 76.2,
  labelType: '4x3',
})

const qrCodeUrl = ref('')

const buildingColumns = ['1', '2', '3', '4', '5', '6', 'P']

function parseBuildingIds(buildingStr: string): number[] {
  if (!buildingStr) return []
  return buildingStr
    .replace(/;/g, ',')
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
    hour12: true,
  })
  return `${day}-${month}-${year} ${time}`
}

const formattedCheckIn = computed(() => formatCheckInPanama(props.checkIn || ''))

const uadmList = computed(() => {
  if (!props.uadms) return []
  return props.uadms.split(';').filter(u => u.trim())
})

async function generateQrCode() {
  if (!props.visitId) return
  try {
    qrCodeUrl.value = await QRCode.toDataURL(props.visitId.toString(), {
      width: 150,
      margin: 1,
    })
  } catch (e) {
    console.error('Error generating QR:', e)
  }
}

onMounted(() => {
  generateQrCode()
})
</script>

<template>
  <div class="flex justify-center items-start visitor-badge-wrapper">
    <!-- ========== PLANTILLA 4x3 (101.6 x 76.2mm) ========== -->
    <div
      v-if="labelType === '4x3'"
      class="bg-white overflow-hidden"
      :style="{ width: '101.6mm', height: '76.2mm' }"
    >
      <div class="h-full flex flex-col">
        <!-- Header VISITANTE -->
        <div style="font-size: 28px; line-height: 1.1; background-color: #000; color: #fff; text-align: center; font-weight: bold; padding: 3px;">
          V I S I T A N T E
        </div>

        <!-- Content Area -->
        <div class="flex-1 p-2 flex flex-col gap-0.5">
          <!-- Name & CED -->
          <div class="text-center">
            <p class="font-bold text-gray-900 uppercase" style="font-size: 14pt; line-height: 1.2;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p class="text-gray-900" style="font-size: 10pt;">
              CED: {{ idCardNumber }} | {{ formattedCheckIn }}
            </p>
          </div>

          <!-- UADM Section -->
          <div style="font-size: 7.5pt; font-weight: bold; background-color: #eee; border-bottom: 1px solid #000; padding: 1px 2px;">
            UNIDAD ADMINISTRATIVA VISITADA
          </div>
          <div class="text-gray-900 font-bold" style="font-size: 7pt; line-height: 1.1; margin: 0.5px 0;">
            <span v-for="(uadm, idx) in uadmList" :key="idx">• {{ uadm }}<br /></span>
          </div>

          <!-- Bottom Row: QR + Buildings + Logo -->
          <div class="flex items-center justify-between mt-auto" style="margin-top: 2px;">
            <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR" style="width: 16mm; height: 16mm;" />
            <div style="flex: 1; margin: 0 3px;">
              <div style="font-size: 7.5pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px;">
                EDIFICIOS AUTORIZADOS
              </div>
              <table style="width: 100%; border-collapse: collapse; border: 1px solid #000; margin-top: 1px;">
                <thead>
                  <tr>
                    <th v-for="(col, idx) in buildingColumns" :key="idx"
                        style="background-color: #f0f0f0; font-size: 8pt; border: 0.5px solid #000; text-align: center; font-weight: bold; width: 14.28%;">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td v-for="(col, idx) in buildingColumns" :key="idx"
                        :style="{
                          height: '18px',
                          width: '14.28%',
                          backgroundColor: isBuildingSelected(idx) ? '#000' : '#fff',
                          border: '0.5px solid #000',
                        }">
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <img src="/img/logo_negro_blanco.png" alt="AMP" style="width: 14mm; max-height: 12mm;" />
          </div>
        </div>
      </div>
    </div>

    <!-- ========== PLANTILLA 3x4 (76.2 x 101.6mm) ========== -->
    <div
      v-else-if="labelType === '3x4'"
      class="bg-white overflow-hidden"
      :style="{ width: '76.2mm', height: '101.6mm' }"
    >
      <div class="h-full flex flex-col">
        <!-- Header VISITANTE -->
        <div style="font-size: 28px; line-height: 1.1; background-color: #000; color: #fff; text-align: center; font-weight: bold; padding: 4px;">
          V I S I T A N T E
        </div>

        <!-- Content Area -->
        <div class="flex-1 p-3 flex flex-col gap-0.5">
          <!-- Name & CED -->
          <div class="text-center">
            <p class="font-bold text-gray-900 uppercase" style="font-size: 13pt; line-height: 1.2;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p class="text-gray-900" style="font-size: 9pt;">
              CED: {{ idCardNumber }} | {{ formattedCheckIn }}
            </p>
          </div>

          <!-- UADM Section -->
          <div style="font-size: 8pt; font-weight: bold; background-color: #eee; border-bottom: 1px solid #000; padding: 1px 2px;">
            UNIDAD ADMINISTRATIVA VISITADA
          </div>
          <div class="text-gray-900 font-bold" style="font-size: 8pt; line-height: 1.1; margin: 0.5px 0; max-height: 18mm; overflow: hidden;">
            <span v-for="(uadm, idx) in uadmList" :key="idx">• {{ uadm }}<br /></span>
          </div>

          <!-- Buildings Section -->
          <div style="font-size: 8pt; font-weight: bold; background-color: #eee; border-bottom: 0.5px solid #000; padding: 1px 2px; margin-top: 1mm;">
            EDIFICIOS AUTORIZADOS
          </div>
          <table style="width: 100%; border-collapse: collapse; border: 0.5px solid #000; margin-top: 1px;">
            <thead>
              <tr>
                <th v-for="(col, idx) in buildingColumns" :key="idx"
                    style="background-color: #f0f0f0; font-size: 7.5pt; border: 0.5px solid #000; text-align: center; font-weight: bold; width: 14.28%;">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td v-for="(col, idx) in buildingColumns" :key="idx"
                    :style="{
                      height: '16px',
                      width: '14.28%',
                      backgroundColor: isBuildingSelected(idx) ? '#000' : '#fff',
                      border: '0.5px solid #000',
                    }">
                </td>
              </tr>
            </tbody>
          </table>

          <!-- QR + Logo -->
          <div class="flex items-center justify-between mt-auto" style="margin-top: auto;">
            <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR" style="width: 16mm; height: 16mm;" />
            <img src="/img/logo_negro_blanco.png" alt="AMP" style="width: 14mm; max-height: 10mm;" />
          </div>
        </div>
      </div>
    </div>

    <!-- ========== PLANTILLA 2x4 (57.15 x 101.6mm) ========== -->
    <div
      v-else-if="labelType === '2x4'"
      class="bg-white overflow-hidden"
      :style="{ width: '57.15mm', height: '101.6mm' }"
    >
      <div class="h-full flex flex-col">
        <!-- Header VISITANTE -->
        <div style="font-size: 26px; line-height: 1; background-color: #000; color: #fff; text-align: center; font-weight: bold; padding: 3px;">
          V I S I T A N T E
        </div>

        <!-- Content Area -->
        <div class="flex-1 p-2 flex flex-col gap-0.5">
          <!-- Name & CED -->
          <div class="text-center">
            <p class="font-bold text-gray-900 uppercase" style="font-size: 12pt; line-height: 1.1;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p class="text-gray-900" style="font-size: 9pt;">
              CED: {{ idCardNumber }}
            </p>
            <p class="text-gray-900" style="font-size: 7.5pt;">
              {{ formattedCheckIn }}
            </p>
          </div>

          <!-- UADM Section -->
          <div style="font-size: 7.5pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px;">
            UNIDAD ADMINISTRATIVA VISITADA
          </div>
          <div class="text-gray-900 font-bold" style="font-size: 7pt; line-height: 1.1; margin: 0.5px 0; max-height: 16mm; overflow: hidden;">
            <span v-for="(uadm, idx) in uadmList" :key="idx">• {{ uadm }}<br /></span>
          </div>

          <!-- Buildings Table (full width) -->
          <div style="font-size: 7.5pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px;">
            EDIFICIOS AUTORIZADOS
          </div>
          <table style="width: 100%; border-collapse: collapse; border: 0.5px solid #000;">
            <thead>
              <tr>
                <th v-for="(col, idx) in buildingColumns" :key="idx"
                    style="background-color: #f0f0f0; font-size: 7.5pt; border: 0.5px solid #000; text-align: center; font-weight: bold; width: 14.28%;">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td v-for="(col, idx) in buildingColumns" :key="idx"
                    :style="{
                      height: '15px',
                      width: '14.28%',
                      backgroundColor: isBuildingSelected(idx) ? '#000' : '#fff',
                      border: '0.5px solid #000',
                    }">
                </td>
              </tr>
            </tbody>
          </table>

          <!-- QR + Logo -->
          <div class="flex items-center justify-between mt-auto" style="margin-top: 2px;">
            <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR" style="width: 15mm; height: 15mm;" />
            <img src="/img/logo_negro_blanco.png" alt="AMP" style="width: 13mm; max-height: 9mm;" />
          </div>
        </div>
      </div>
    </div>

    <!-- ========== PLANTILLA 4x2 (101.6 x 57.15mm) ========== -->
    <div
      v-else-if="labelType === '4x2'"
      class="bg-white overflow-hidden"
      :style="{ width: '101.6mm', height: '57.15mm' }"
    >
      <div class="h-full flex flex-row">
        <!-- Left: VISITANTE vertical -->
        <div style="width: 9mm; background-color: #000; color: #fff; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
          <div style="writing-mode: vertical-rl; text-orientation: mixed; font-size: 18px; font-weight: bold; letter-spacing: 2px;">
            V I S I T A N T E
          </div>
        </div>

        <!-- Right: Content -->
        <div class="flex-1 p-2 flex flex-col gap-0.5 overflow-hidden">
          <!-- Name & CED -->
          <div class="text-center">
            <p class="font-bold text-gray-900 uppercase" style="font-size: 12pt; line-height: 1.1;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p class="text-gray-900" style="font-size: 8pt;">
              CED: {{ idCardNumber }} | {{ formattedCheckIn }}
            </p>
          </div>

          <!-- UADM Section -->
          <div style="font-size: 7pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px;">
            UNIDAD ADMINISTRATIVA VISITADA
          </div>
          <div class="text-gray-900 font-bold" style="font-size: 6.5pt; line-height: 1; max-height: 8mm; overflow: hidden;">
            <span v-for="(uadm, idx) in uadmList" :key="idx">• {{ uadm }}<br /></span>
          </div>

          <!-- Bottom Row: QR + Buildings + Logo -->
          <div class="flex items-center justify-between" style="margin-top: auto;">
            <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="QR" style="width: 15mm; height: 15mm;" />
            <div style="flex: 1; margin: 0 2px;">
              <div style="font-size: 7pt; font-weight: bold; background-color: #eee; border-bottom: 0.4px solid #000; padding: 1px 2px;">
                EDIFICIOS AUTORIZADOS
              </div>
              <table style="width: 100%; border-collapse: collapse; border: 0.5px solid #000; margin-top: 0.5px;">
                <thead>
                  <tr>
                    <th v-for="(col, idx) in buildingColumns" :key="idx"
                        style="background-color: #f0f0f0; font-size: 7pt; border: 0.5px solid #000; text-align: center; font-weight: bold; width: 14.28%;">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td v-for="(col, idx) in buildingColumns" :key="idx"
                        :style="{
                          height: '12px',
                          width: '14.28%',
                          backgroundColor: isBuildingSelected(idx) ? '#000' : '#fff',
                          border: '0.5px solid #000',
                        }">
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <img src="/img/logo_negro_blanco.png" alt="AMP" style="width: 13mm; max-height: 9mm;" />
          </div>
        </div>
      </div>
    </div>

    <!-- Fallback: Default 4x3 -->
    <div
      v-else
      class="bg-white overflow-hidden"
      :style="{ width: '101.6mm', height: '76.2mm' }"
    >
      <div class="h-full flex flex-col">
        <div style="font-size: 28px; line-height: 1.1; background-color: #000; color: #fff; text-align: center; font-weight: bold; padding: 3px;">
          V I S I T A N T E
        </div>
        <div class="flex-1 p-2 flex flex-col gap-0.5">
          <div class="text-center">
            <p class="font-bold text-gray-900 uppercase" style="font-size: 14pt;">
              {{ visitorName?.toUpperCase() || 'N/A' }}
            </p>
            <p style="font-size: 10pt;">CED: {{ idCardNumber }} | {{ formattedCheckIn }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  .visitor-badge-wrapper {
    display: flex !important;
    justify-content: center !important;
    align-items: flex-start !important;
  }
}
</style>