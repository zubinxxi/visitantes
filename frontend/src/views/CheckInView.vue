<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import api from '@/lib/api'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import VisitorBadge from '@/components/VisitorBadge.vue'
import BadgePrintPreview from '@/components/BadgePrintPreview.vue'
import { LABEL_SIZES, type LabelSize } from '@/types/labelSize'
import type { Visit } from '@/types/visit'
import Multiselect from 'vue-multiselect'

const { success, error: showError } = useToast()
const auth = useAuthStore()

interface ParsedVisitor {
  id_card_number: string
  names: string
  surnames: string
  gender: string
  province: string
  nationality: string
  id_num_control: string
}

interface Visitor {
  id: number
  names: string
  surnames: string
  id_card_number: string
  photo: string
  gender: string
  province: string
  nationality: string
}

interface Uadm { id: number; name: string }
interface Building { id: number; description: string }

const labelSizes: readonly LabelSize[] = LABEL_SIZES
const defaultSize: LabelSize = LABEL_SIZES[0] as LabelSize
const selectedLabelSize = ref<LabelSize>({ ...defaultSize })

const loading = ref(false)
const processingQr = ref(false)
const qrInput = ref('')
const qrInputRef = ref<HTMLInputElement | null>(null)
const qrScanned = ref(false)
const needsRegistration = ref(false)
const currentVisitor = ref<Visitor | null>(null)
const currentVisit = ref<{ id: number; check_in: string } | null>(null)
const parsedData = ref<ParsedVisitor | null>(null)
const showBadge = ref(false)
const showBadgeModal = ref(false)
interface BadgeData {
  visit_id: number
  visitor_name: string
  id_card_number: string
  check_in: string
  uadms: string
  buildings: string
}

const badgeData = ref<BadgeData | null>(null)
const badgeVisit = ref<Visit | null>(null)
const confirmCompanyRepresents = ref('')
const confirmPurpose = ref('')

const uadmOptions = ref<Uadm[]>([])
const buildingOptions = ref<Building[]>([])
const genderOptions = [
  { value: 'M', label: 'Masculino' },
  { value: 'F', label: 'Femenino' },
]

function getGenderObject(value: string) {
  return genderOptions.find(g => g.value === value) || null
}

function getPhotoUrl(photoPath: string | null): string {
  if (!photoPath) return ''
  if (photoPath.startsWith('data:')) return photoPath
  if (photoPath.startsWith('http')) return photoPath + '?t=' + Date.now()
  return `${photoPath}?t=${Date.now()}`
}
const selectedUadms = ref<Uadm[]>([])
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const uadmSelectRef = ref<any>(null)

const selectedBuildings = ref<Building[]>([])
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const buildingSelectRef = ref<any>(null)

function onSelect(ref: { close: () => void }) {
  setTimeout(() => ref.close(), 0)
}

const showRegisterForm = ref(false)
const registerForm = ref({
  names: '',
  surnames: '',
  gender: getGenderObject('M'),
  id_card_number: '',
  id_num_control: '',
  province: '',
  nationality: '',
  company_represents: '',
  purpose: '',
  photo: '',
})

const showCamera = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const stream = ref<MediaStream | null>(null)
const photoRequired = ref(false)

async function loadOptions() {
  try {
    const [uadmRes, buildingRes] = await Promise.all([
      api.get('/maintenance/uadms/', { params: { limit: 100 } }),
      api.get('/maintenance/buildings/', { params: { limit: 100 } }),
    ])
    uadmOptions.value = uadmRes.data.items || uadmRes.data
    buildingOptions.value = buildingRes.data.items || buildingRes.data
  } catch (e) {
    console.error('Error loading options:', e)
  }
}

async function startCamera() {
  try {
    if (stream.value) {
      stopCamera()
    }
    stream.value = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        facingMode: 'user',
        width: { ideal: 640 },
        height: { ideal: 480 }
      } 
    })
    
    await nextTick()
    
    setTimeout(() => {
      if (videoRef.value) {
        videoRef.value.srcObject = stream.value
      }
    }, 100)
    
    showCamera.value = true
    photoRequired.value = true
  } catch (e) {
    console.error('Camera error:', e)
    showError('No se pudo acceder a la cámara')
  }
}

function focusQrInput() {
  if (!qrScanned.value) {
    nextTick(() => {
      qrInputRef.value?.focus()
    })
  }
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
  qrScanned.value = true
  try {
    await processQr(value)
    qrInput.value = ''
  } catch (err: unknown) {
    qrScanned.value = false
    qrInput.value = ''
    let msg = 'Error al procesar QR'
    if (err && typeof err === 'object' && 'response' in err) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      if (detail) msg = detail
    } else if (err instanceof Error) {
      msg = err.message
    }
    showError(msg)
  } finally {
    processingQr.value = false
  }
}

async function processQr(rawData: string) {
  loading.value = true
  try {
    const response = await api.post('/checkin/process-qr', { raw_data: rawData })
    const data = response.data
    
    if (data.needs_registration) {
      needsRegistration.value = true
      parsedData.value = data.visitor_data
      registerForm.value = {
        names: data.visitor_data.names || '',
        surnames: data.visitor_data.surnames || '',
        gender: getGenderObject(data.visitor_data.gender || 'M'),
        id_card_number: data.visitor_data.id_card_number || '',
        id_num_control: data.visitor_data.id_num_control || '',
        province: data.visitor_data.province || '',
        nationality: data.visitor_data.nationality || '',
        company_represents: '',
        purpose: '',
        photo: '',
      }
      showRegisterForm.value = true
    } else {
      needsRegistration.value = false
      currentVisitor.value = {
        ...data.visitor,
        photo: getPhotoUrl(data.visitor.photo)
      }
      currentVisit.value = data.visit
      await loadOptions()
    }
    
    success('QR procesado correctamente')
  } catch (err: any) {
    let msg = 'Error al procesar QR'
    if (err.response?.data?.detail) {
      msg = err.response.data.detail
    } else if (err.message) {
      msg = err.message
    }
    
    console.error('Error processing QR:', err)
    showError(msg)
    resetForm()
  } finally {
    loading.value = false
  }
}

function stopCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
  showCamera.value = false
}

function takePhoto() {
  if (!videoRef.value || !canvasRef.value) return
  
  const video = videoRef.value
  const canvas = canvasRef.value
  
  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
  
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    registerForm.value.photo = canvas.toDataURL('image/jpeg', 0.8)
  }
  photoRequired.value = false
  stopCamera()
}

async function registerAndCheckIn() {
  if (!registerForm.value.photo) {
    photoRequired.value = true
    showError('La foto es obligatoria')
    return
  }
  
  loading.value = true
  try {
    let photoUrl = registerForm.value.photo
    
    if (registerForm.value.photo.startsWith('data:')) {
      const formData = new FormData()
      const blob = await fetch(registerForm.value.photo).then(r => r.blob())
      formData.append('file', new File([blob], `${registerForm.value.id_card_number}.jpg`, { type: 'image/jpeg' }))
      
      try {
        const uploadRes = await api.post('/visitors/upload-photo-temp', formData, {
          params: { cedula: registerForm.value.id_card_number }
        })
        photoUrl = uploadRes.data.url
      } catch (e) {
        console.error('Error uploading photo:', e)
      }
    }
    
    const userLogin = auth.user?.login || 'sysadmin'
    const genderValue = registerForm.value.gender?.value || 'M'
    
    const visitorRes = await api.post('/visitors/', {
      names: registerForm.value.names,
      surnames: registerForm.value.surnames,
      gender: genderValue,
      id_card_number: registerForm.value.id_card_number,
      id_num_control: registerForm.value.id_num_control,
      province: registerForm.value.province,
      nationality: registerForm.value.nationality,
      photo: photoUrl,
      user_created: userLogin,
    })
    
    showRegisterForm.value = false
    currentVisit.value = null
    
    currentVisitor.value = {
      id: visitorRes.data.id,
      names: registerForm.value.names,
      surnames: registerForm.value.surnames,
      id_card_number: registerForm.value.id_card_number,
      photo: photoUrl,
      gender: genderValue,
      province: registerForm.value.province,
      nationality: registerForm.value.nationality,
    }
    
    await loadOptions()
    
    success('Visitante registrado. Seleccione UADMs y Edificios para confirmar')
  } catch (err: unknown) {
    let msg = 'Error al registrar visitante'
    if (err && typeof err === 'object' && 'response' in err) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      if (detail) msg = detail
    } else if (err instanceof Error) {
      msg = err.message
    }
    showError(msg)
  } finally {
    loading.value = false
  }
}

function confirmCheckIn() {
  if (!currentVisitor.value) return
  
  const uadmIds = selectedUadms.value.map((u) => u.id)
  const buildingIds = selectedBuildings.value.map((b) => b.id)
  
  loading.value = true
  const payload: { visitor_id: number; uadm_ids: number[]; building_ids: number[]; company_represents: string; purpose: string } = {
    visitor_id: currentVisitor.value.id,
    uadm_ids: uadmIds,
    building_ids: buildingIds,
    company_represents: confirmCompanyRepresents.value,
    purpose: confirmPurpose.value,
  }
  
  api.post('/checkin/confirm', payload)
  .then(async (response) => {
    const visitId = response.data.id
    const checkInTime = response.data.check_in
    currentVisit.value = { id: visitId, check_in: checkInTime }
    
    const badgeRes = await api.get(`/checkin/visits/${visitId}/badge`)
    badgeData.value = badgeRes.data
    badgeVisit.value = {
      id: visitId,
      id_visitors: currentVisitor.value!.id,
      id_type_of_proce: 6,
      company_represents: confirmCompanyRepresents.value,
      purpose: confirmPurpose.value,
      buildings_visited: selectedBuildings.value.map((b) => String(b.id)).join(','),
      uadm_visited: selectedUadms.value.map((u) => String(u.id)).join(';'),
      check_in: checkInTime,
      check_out: null,
      user_created: auth.user?.login || 'sysadmin',
      names: currentVisitor.value!.names,
      surnames: currentVisitor.value!.surnames,
      id_card_number: currentVisitor.value!.id_card_number,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      uadms_names: selectedUadms.value.map((u) => (u as any).name).join(';'),
    }
    showBadgeModal.value = true
    success('Check-in confirmado')
  })
  .catch((err: unknown) => {
    let msg = 'Error al confirmar check-in'
    if (err && typeof err === 'object' && 'response' in err) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
      if (detail) msg = detail
    } else if (err instanceof Error) {
      msg = err.message
    }
    showError(msg)
  })
  .finally(() => {
    loading.value = false
  })
}

function printBadge() {
  const printContent = document.querySelector('.visitor-badge-print-container')?.innerHTML
  if (!printContent) return

  const size = selectedLabelSize.value
  const width = size?.width || 101.6
  const height = size?.height || 76.2

  const printCSS = `
    @page { size: ${width}mm ${height}mm; margin: 0; }
    * { box-sizing: border-box; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    html { height: auto; margin: 0; padding: 0; }
    body {
      margin: 0; padding: 0; height: auto; min-height: 0; overflow: hidden;
      font-family: 'Arial', sans-serif;
    }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #000; padding: 4px; }
    .bg-black { background-color: #000 !important; color: #fff !important; }
    .bg-white { background-color: #fff !important; }
    .bg-gray-200 { background-color: #e5e7eb !important; }
    .flex { display: flex; }
    .flex-row { flex-direction: row; }
    .flex-col { flex-direction: column; }
    .flex-1 { flex: 1 1 0%; }
    .h-full { height: 100%; }
    .items-center { align-items: center; }
    .justify-center { justify-content: center; }
    .justify-between { justify-content: space-between; }
    .gap-0.5 { gap: 2px; }
    .gap-1 { gap: 4px; }
    .mt-auto { margin-top: auto; }
    .w-full { width: 100%; }
    .p-1.5 { padding: 6px; }
    .p-2 { padding: 8px; }
    .p-3 { padding: 12px; }
    .px-1 { padding-left: 4px; padding-right: 4px; }
    .text-center { text-align: center; }
    .text-gray-900 { color: #111827; }
    .font-bold { font-weight: bold; }
    .uppercase { text-transform: uppercase; }
    .overflow-hidden { overflow: hidden; }
    .writing-mode-vertical { writing-mode: vertical-rl; text-orientation: mixed; }
  `

  const printHTML = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Badge de Visitante</title>
  <style>${printCSS}</style>
</head>
<body>${printContent}</body>
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

function handleNewCheckin() {
  showBadgeModal.value = false
  resetForm()
}

function resetForm() {
  qrInput.value = ''
  qrScanned.value = false
  needsRegistration.value = false
  currentVisitor.value = null
  currentVisit.value = null
  parsedData.value = null
  showRegisterForm.value = false
  showBadge.value = false
  showBadgeModal.value = false
  badgeData.value = null
  badgeVisit.value = null
  selectedUadms.value = []
  selectedBuildings.value = []
  confirmCompanyRepresents.value = ''
  confirmPurpose.value = ''
  stopCamera()
  focusQrInput()
}

onMounted(() => {
  loadOptions()
  focusQrInput()
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-medium text-gray-800 dark:text-white">Check-In de Visitantes</h1>
    </div>

    <!-- QR Input Section -->
    <div v-if="!qrScanned" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6 mb-6">
      <h3 class="text-base font-medium text-gray-800 dark:text-white mb-4">Escanear Cédula</h3>
      <p class="text-theme-sm text-gray-500 dark:text-gray-400 mb-4">
        Escanee el código QR de la cédula o ingrese el número de cédula manualmente (ej: 8-7777-8888)
      </p>
      <input
        ref="qrInputRef"
        v-model="qrInput"
        @keydown.enter="handleQrInput"
        @blur="focusQrInput"
        type="text"
        class="h-14 w-full text-lg rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
        placeholder="Escanee o escriba el número de cédula..."
        autofocus
      />
      <div v-if="loading" class="mt-4 flex items-center justify-center">
        <span class="h-6 w-6 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
        <span class="ml-2 text-gray-600 dark:text-gray-400">Procesando...</span>
      </div>
    </div>

    <!-- Registration Form (when visitor doesn't exist) -->
    <div v-if="showRegisterForm" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
      <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <h3 class="text-base font-medium text-gray-800 dark:text-white">Registrar Nuevo Visitante</h3>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">El visitante no existe. Complete los datos y capture la foto.</p>
      </div>
      <form @submit.prevent="registerAndCheckIn" class="p-6 space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Nombres <span class="text-error-500">*</span>
            </label>
            <input
              v-model="registerForm.names"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
              required
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Apellidos <span class="text-error-500">*</span>
            </label>
            <input
              v-model="registerForm.surnames"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
              required
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Cédula <span class="text-error-500">*</span>
            </label>
            <input
              v-model="registerForm.id_card_number"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
              required
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Género
            </label>
            <Multiselect
              v-model="registerForm.gender"
              :options="genderOptions"
              :searchable="false"
              :close-on-select="true"
              placeholder="Seleccione..."
              label="label"
              track-by="value"
              class="multiselect-dark"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Provincia
            </label>
            <input
              v-model="registerForm.province"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Nacionalidad
            </label>
            <input
              v-model="registerForm.nationality"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
            />
          </div>
        </div>

        <!-- Photo Capture -->
        <div>
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Foto <span class="text-error-500">*</span>
          </label>
          <div class="flex gap-3">
            <button
              v-if="!showCamera && !registerForm.photo"
              @click="startCamera"
              type="button"
              class="rounded-lg bg-brand-500 px-4 py-2 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
            >
              Tomar Foto
            </button>
            <div v-if="showCamera" class="space-y-3">
              <video 
                ref="videoRef" 
                autoplay 
                playsinline
                muted
                class="w-full max-w-xs rounded-lg bg-gray-900"
              ></video>
              <canvas ref="canvasRef" class="hidden"></canvas>
              <div class="flex gap-2">
                <button
                  @click="takePhoto"
                  type="button"
                  class="rounded-lg bg-green-500 px-4 py-2 text-theme-sm font-medium text-white"
                >
                  Capturar
                </button>
                <button
                  @click="stopCamera"
                  type="button"
                  class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2 text-theme-sm font-medium text-gray-700 dark:text-gray-200"
                >
                  Cancelar
                </button>
              </div>
            </div>
            <div v-if="registerForm.photo && !showCamera" class="flex items-center gap-3">
              <img :src="registerForm.photo" class="h-20 w-20 object-cover rounded-lg border" />
              <button
                @click="startCamera"
                type="button"
                class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2 text-theme-sm font-medium text-gray-700 dark:text-gray-200"
              >
                Cambiar
              </button>
            </div>
          </div>
          <p v-if="photoRequired" class="text-sm text-error-500 mt-1">La foto es obligatoria</p>
        </div>

        <div class="flex justify-between pt-4">
          <button
            @click="resetForm"
            type="button"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
          >
            {{ loading ? 'Registrando...' : 'Registrar y Check-In' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Confirmation Form (when visitor exists) -->
    <div v-if="currentVisitor && !showRegisterForm && !showBadge" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
      <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <h3 class="text-base font-medium text-gray-800 dark:text-white">Confirmar Check-In</h3>
      </div>
      <div class="p-6 space-y-5">
        <!-- Visitor Info -->
        <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <img
            v-if="currentVisitor?.photo"
            :src="getPhotoUrl(currentVisitor?.photo)"
            class="h-16 w-16 rounded-full object-cover"
          />
          <div v-else class="h-16 w-16 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
            <span class="text-2xl text-gray-500">{{ currentVisitor?.names?.charAt(0) }}</span>
          </div>
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ currentVisitor?.names }} {{ currentVisitor?.surnames }}</p>
            <p class="text-sm text-gray-500">{{ currentVisitor?.id_card_number }}</p>
          </div>
        </div>

        <!-- UADM Selection -->
        <div>
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Unidades Administrativas <span class="text-error-500">*</span>
          </label>
          <Multiselect
            ref="uadmSelectRef"
            v-model="selectedUadms"
            :options="uadmOptions"
            :multiple="true"
            :close-on-select="true"
            @select="() => onSelect(uadmSelectRef)"
            placeholder="Seleccione..."
            label="name"
            track-by="id"
            class="multiselect-dark"
          />
        </div>

<!-- Buildings Selection -->
        <div>
          <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
            Edificios
          </label>
          <Multiselect
            ref="buildingSelectRef"
            v-model="selectedBuildings"
            :options="buildingOptions"
            :multiple="true"
            :close-on-select="true"
            @select="() => onSelect(buildingSelectRef)"
            placeholder="Seleccione..."
            label="description"
            track-by="id"
            class="multiselect-dark"
          />
        </div>

        <!-- Company and Purpose -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Empresa que representa
            </label>
            <input
              v-model="confirmCompanyRepresents"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
              placeholder="Empresa o institución"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Propósito de la visita
            </label>
            <input
              v-model="confirmPurpose"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100"
              placeholder="Motivo de la visita"
            />
          </div>
        </div>

        <div class="flex justify-between pt-4">
          <button
            @click="resetForm"
            type="button"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs"
          >
            Cancelar
          </button>
          <button
            @click="confirmCheckIn"
            :disabled="loading || selectedUadms.length === 0"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
          >
            {{ loading ? 'Confirmando...' : 'Confirmar Check-In' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Badge Preview & Print -->
    <div v-if="showBadge && badgeData" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6">
      <h3 class="text-base font-medium text-gray-800 dark:text-white mb-4">Badge de Visitante</h3>
      
      <div class="mb-4 no-print">
        <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
          Tamaño de etiqueta
        </label>
        <Multiselect
          v-model="selectedLabelSize"
          :options="labelSizes"
          :searchable="false"
          :close-on-select="true"
          placeholder="Seleccione..."
          label="label"
          track-by="value"
          class="multiselect-dark"
        />
      </div>
      
      <div class="visitor-badge-print-container">
        <VisitorBadge
          :visit-id="badgeData.visit_id"
          :visitor-name="badgeData.visitor_name"
          :id-card-number="badgeData.id_card_number"
          :check-in="badgeData.check_in"
          :uadms="badgeData.uadms"
          :buildings="badgeData.buildings"
          :label-type="selectedLabelSize?.value"
        />
      </div>
      
      <div class="flex justify-center gap-3 mt-6 no-print">
        <button
          @click="printBadge"
          class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
        >
          Imprimir Badge
        </button>
        <button
          @click="handleNewCheckin"
          class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs"
        >
          Nueva Visita
        </button>
      </div>
    </div>

    <BadgePrintPreview
      v-model="showBadgeModal"
      :visits="badgeVisit ? [badgeVisit] : []"
      close-label="Nueva Visita"
      @close="handleNewCheckin"
    />
  </div>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }

  body {
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
  }

  body > *:not(.visitor-badge-print-container) {
    display: none !important;
  }

  .visitor-badge-print-container {
    position: absolute;
    left: 0;
    top: 0;
  }
}
</style>