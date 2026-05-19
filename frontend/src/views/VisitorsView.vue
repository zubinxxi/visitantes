<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import api from '@/lib/api'
import type { Visitor } from '@/types/visit'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import Multiselect from 'vue-multiselect'

const toast = useToast()
const auth = useAuthStore()

const limitOptions = [
  { value: 10, label: '10' },
  { value: 25, label: '25' },
  { value: 50, label: '50' },
  { value: 100, label: '100' },
]

const searchQuery = ref('')
const results = ref<Visitor[]>([])
const loading = ref(false)
const searched = ref(false)
const selectedVisitor = ref<Visitor | null>(null)
const showDetails = ref(false)
const showForm = ref(false)
const editingVisitor = ref<Visitor | null>(null)
const showDeleteConfirm = ref(false)
const deletingVisitor = ref<Visitor | null>(null)

const limit = ref(10)
const page = ref(1)
const totalPages = ref(1)
const total = ref(0)

const itemsWithLineNum = computed(() => {
  const start = (page.value - 1) * limit.value
  return results.value.map((item, index) => ({
    ...item,
    line_num: start + index + 1
  }))
})

function getPhotoUrl(photoPath: string | null): string {
  if (!photoPath) return ''
  if (photoPath.startsWith('data:')) return photoPath
  // If it's already a full URL, return as is
  if (photoPath.startsWith('http')) return photoPath + '?t=' + Date.now()
  return `${photoPath}?t=${Date.now()}`
}

// Opciones para género
const genderOptions = [
  { value: 'M', label: 'Masculino' },
  { value: 'F', label: 'Femenino' }
]

// Opciones para provincia (cargadas desde API)
const provinceOptions = ref<{ value: string; label: string }[]>([])

async function loadProvinces(search?: string) {
  try {
    const params: Record<string, unknown> = { limit: 100 }
    if (search) params.search = search
    const response = await api.get('/maintenance/provinces/', { params })
    provinceOptions.value = response.data.items.map((p: Record<string, any>) => ({
      value: p.description,
      label: p.description
    }))
  } catch (error) {
    console.error('Error loading provinces:', error)
  }
}

function searchProvince(query: string) {
  loadProvinces(query)
}

const form = ref<Record<string, unknown>>({
  names: '',
  surnames: '',
  gender: '',
  id_card_number: '',
  id_num_control: '',
  province: '',
  nationality: '',
  photo: '',
})

const formPhoto = computed(() => typeof form.value.photo === 'string' ? form.value.photo : '')
const formNames = computed(() => typeof form.value.names === 'string' ? form.value.names : '')

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const stream = ref<MediaStream | null>(null)
const photoRequired = ref(false)
const showCamera = ref(false)

async function loadItems(newPage?: number, newLimit?: number) {
  loading.value = true
  searched.value = true

  try {
    const params = new URLSearchParams()
    params.set('page', String(newPage ?? page.value))
    params.set('limit', String(newLimit ?? limit.value))
    if (searchQuery.value.trim()) {
      params.set('search', searchQuery.value)
    }

    const response = await api.get(`/visitors/?${params.toString()}`)
    results.value = response.data.items
    total.value = response.data.total
    page.value = response.data.page
    limit.value = response.data.limit
    totalPages.value = response.data.total_pages
  } catch (error) {
    console.error('Error al listar visitantes:', error)
  } finally {
    loading.value = false
  }
}

function changePage(newPage: number) {
  if (newPage >= 1 && newPage <= totalPages.value) {
    loadItems(newPage)
  }
}

function changeLimit(newLimit: any) {
  const limitVal = newLimit && typeof newLimit === 'object' ? newLimit.value : newLimit
  loadItems(1, limitVal)
}

function setSearch(value: string) {
  searchQuery.value = value
  loadItems(1, limit.value)
}

function viewDetails(visitor: Visitor) {
  selectedVisitor.value = visitor
  showDetails.value = true
}

function openCreate() {
  editingVisitor.value = null
  form.value = {
    names: '',
    surnames: '',
    gender: '',
    id_card_number: '',
    id_num_control: '',
    province: '',
    nationality: '',
    photo: '',
  }
  photoRequired.value = false
  showCamera.value = false
  showForm.value = true
  loadProvinces()
}

function getGenderObject(value: string) {
  return genderOptions.find(g => g.value === value) || null
}

function getProvinceObject(value: string) {
  return provinceOptions.value.find(p => p.value === value) || null
}

function openEdit(visitor: Visitor) {
  editingVisitor.value = visitor
  form.value = {
    names: visitor.names || '',
    surnames: visitor.surnames || '',
    gender: getGenderObject(visitor.gender || '') as { value: string; label: string } | null,
    id_card_number: visitor.id_card_number || '',
    id_num_control: visitor.id_num_control || '',
    province: getProvinceObject(visitor.province || '') as { value: string; label: string } | null,
    nationality: visitor.nationality || '',
    photo: visitor.photo || '',
  }
  photoRequired.value = false
  showCamera.value = false
  showForm.value = true
  loadProvinces()
}

function confirmDelete(visitor: Visitor) {
  deletingVisitor.value = visitor
  showDeleteConfirm.value = true
}

function closeDelete() {
  showDeleteConfirm.value = false
  deletingVisitor.value = null
}

function confirmDeleteAction() {
  if (deletingVisitor.value) {
    deleteVisitor(deletingVisitor.value)
  }
  closeDelete()
}

async function deleteVisitor(visitor: Visitor) {
  try {
    await api.delete(`/visitors/${visitor.id}`)
    toast.success('Visitante eliminado correctamente')
    loadItems()
  } catch (error: unknown) {
    console.error('Error deleting visitor:', error)
    const errMsg = error instanceof Error ? error.message : 'Error al eliminar visitante'
    toast.error(errMsg)
  }
}

function closeForm() {
  showForm.value = false
  editingVisitor.value = null
  stopCamera()
}

async function startCamera() {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
    }
  } catch (error) {
    console.error('Error al iniciar cámara:', error)
    toast.error('No se pudo acceder a la cámara')
  }
}

function stopCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
}

function takePhoto() {
  if (videoRef.value && canvasRef.value) {
    const video = videoRef.value
    const canvas = canvasRef.value
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(video, 0, 0)
      const dataUrl = canvas.toDataURL('image/jpeg')
      form.value.photo = dataUrl
      photoRequired.value = false
      showCamera.value = false
    }
  }
}

function toggleCamera() {
  showCamera.value = !showCamera.value
  if (showCamera.value) {
    nextTick(() => {
      startCamera()
    })
  } else {
    stopCamera()
  }
}

function getPhotoString(): string {
  return typeof form.value.photo === 'string' ? form.value.photo : ''
}

function dataURLtoFile(dataurl: string, filename: string): File {
  const arr = dataurl.split(',')
  const firstPart = arr[0] || ''
  const mimeMatch = firstPart.match(/:(.*?);/)
  const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg'
  const bstr = atob(arr[1] || '')
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new File([u8arr], filename, { type: mime })
}

async function uploadPhotoWithCedula(cedula: string): Promise<string | null> {
  const photoStr = getPhotoString()
  if (!photoStr || !photoStr.startsWith('data:')) return null

  const file = dataURLtoFile(photoStr, `${cedula}.jpg`)
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post(`/visitors/upload-photo-temp`, formData, {
      params: { cedula: cedula }
    })
    return response.data.url
  } catch (error) {
    console.error('Error uploading photo:', error)
    return null
  }
}

async function saveVisitor() {
  const photoStr = getPhotoString()
  if (!photoStr) {
    photoRequired.value = true
    toast.error('La foto es obligatoria')
    return
  }

  if (!form.value.id_card_number) {
    toast.error('La cédula es obligatoria para guardar la foto')
    return
  }

try {
    let photoUrl = photoStr

    if (photoStr.startsWith('data:')) {
      const uploadedUrl = await uploadPhotoWithCedula(String(form.value.id_card_number))
      if (!uploadedUrl) {
        toast.error('Error al subir la foto')
        return
      }
      photoUrl = uploadedUrl
    }

        const genderValue = typeof form.value.gender === 'object' && form.value.gender ? String((form.value.gender as Record<string, string>).value || '') : String(form.value.gender || '')
    const provinceValue = typeof form.value.province === 'object' && form.value.province ? String((form.value.province as Record<string, string>).value || '') : String(form.value.province || '')

    const payload = {
      names: form.value.names,
      surnames: form.value.surnames,
      gender: genderValue,
      id_card_number: form.value.id_card_number,
      id_num_control: form.value.id_num_control,
      province: provinceValue,
      nationality: form.value.nationality,
      photo: photoUrl,
      user_created: auth.user?.login || 'admin'
    }
    console.log('Payload:', payload)

    if (editingVisitor.value) {
      console.log('PUT /visitors/', editingVisitor.value.id)
      await api.put(`/visitors/${editingVisitor.value.id}`, payload)
      toast.success('Visitante actualizado correctamente')
    } else {
      console.log('POST /visitors/')
      await api.post('/visitors/', payload)
      toast.success('Visitante registrado correctamente')
    }
    closeForm()
    loadItems()
  } catch (error: unknown) {
    console.error('Error saving visitor:', error)
    const errMsg = error instanceof Error ? error.message : 'Error al guardar visitante'
    toast.error(errMsg)
  }
}

onMounted(() => {
  loadItems()
  loadProvinces()
})

onUnmounted(stopCamera)
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Visitantes</h1>
      </div>
      <button
        @click="openCreate"
        class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo Visitante
      </button>
    </div>

    <!-- Search Bar -->
    <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6 mb-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            @keyup.enter="setSearch(searchQuery)"
            @input="setSearch(searchQuery)"
            type="text"
            placeholder="Buscar por nombre o cédula"
            class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent pl-10 pr-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
          />
        </div>

      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <!-- No results -->
    <div
      v-else-if="searched && results.length === 0"
      class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-medium text-gray-900 dark:text-white">Sin resultados</h3>
      <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">No se encontraron visitantes con ese criterio</p>
    </div>

    <!-- Results Table -->
    <div v-else-if="results.length > 0" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">#</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Visitante</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Cédula</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Provincia</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Nacionalidad</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400 w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="visitor in itemsWithLineNum" :key="visitor.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visitor.line_num }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="h-10 w-10 rounded-full overflow-hidden border-2 border-gray-200 dark:border-gray-700 bg-gray-100">
                    <img 
                      v-if="visitor.photo" 
                      :src="getPhotoUrl(visitor.photo)"
                      :key="visitor.photo"
                      :alt="visitor.names"
                      class="w-full h-full object-cover"
                      @error="(e: Event) => (e.target as HTMLImageElement).src = ''"
                    />
                    <div 
                      v-else 
                      class="flex h-full w-full items-center justify-center bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-theme-sm"
                    >
                      {{ visitor.names?.charAt(0) || '?' }}{{ visitor.surnames?.charAt(0) || '' }}
                    </div>
                  </div>
                  <div>
                    <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ visitor.names }} {{ visitor.surnames }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visitor.id_card_number }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visitor.province }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visitor.nationality }}</td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <!-- Edit Button -->
                  <button
                    @click="openEdit(visitor)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                    title="Editar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <!-- View Details Button -->
                  <button
                    @click="viewDetails(visitor)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                    title="Ver detalles"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                    </svg>
                  </button>
                  <!-- Delete Button -->
                  <button
                    @click="confirmDelete(visitor)"
                    class="rounded-lg p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                    title="Eliminar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 21V5a2 2 0 012-2h4l2 2h4a2 2 0 012 2v2M10 11v6m4-6v6" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-gray-100 dark:border-gray-800 px-6 py-4">
        <div class="flex items-center gap-2 text-theme-sm text-gray-500 dark:text-gray-400">
          <span>Mostrando</span>
          <Multiselect
            :model-value="limitOptions.find(o => o.value === limit)"
            @update:model-value="changeLimit"
            :options="limitOptions"
            :searchable="false"
            :close-on-select="true"
            :show-labels="false"
            label="label"
            track-by="value"
            class="multiselect-dark w-20"
          />
          <span>de {{ total }} registros</span>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="changePage(page - 1)"
            :disabled="page <= 1"
            class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <template v-for="p in totalPages" :key="p">
            <button
              v-if="p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1)"
              @click="changePage(p)"
              :class="[
                'rounded-lg px-3 py-1.5 text-theme-sm font-medium transition-colors',
                p === page
                  ? 'bg-brand-500 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              ]"
            >
              {{ p }}
            </button>
            <span v-else-if="p === page - 2 || p === page + 2" class="px-1 text-gray-400">...</span>
          </template>
          <button
            @click="changePage(page + 1)"
            :disabled="page >= totalPages"
            class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="showDetails && selectedVisitor"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm"
      @click.self="showDetails = false"
    >
      <div class="w-full max-w-md mx-4 overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">Detalles del Visitante</h3>
          <button @click="showDetails = false" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div class="flex items-center gap-4 mb-6">
            <div class="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-bold text-xl">
              {{ selectedVisitor.names?.charAt(0) || '?' }}
            </div>
            <div>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedVisitor.names }} {{ selectedVisitor.surnames }}</p>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ selectedVisitor.id_card_number }}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Género</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisitor.gender === 'M' ? 'Masculino' : 'Femenino' }}</p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Provincia</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisitor.province }}</p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Nacionalidad</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisitor.nationality }}</p>
            </div>
            <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-3">
              <p class="text-theme-xs text-gray-500 dark:text-gray-400 mb-1">Registrado por</p>
              <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ selectedVisitor.user_created }}</p>
            </div>
          </div>
        </div>
        <div class="flex justify-end border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="showDetails = false"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div
      v-if="showForm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm"
      @click.self="closeForm"
    >
      <div class="w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            {{ editingVisitor ? 'Editar Visitante' : 'Nuevo Visitante' }}
          </h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Photo Section -->
            <div class="md:col-span-2">
              <label class="mb-2 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Foto del Visitante <span class="text-error-500">*</span>
              </label>
              <div class="flex flex-col items-center gap-4">
                <!-- Show existing photo or new photo captured -->
                <div v-if="!showCamera" class="relative w-48 h-48 rounded-full overflow-hidden border-2 border-gray-300 dark:border-gray-600 bg-gray-100">
                  <img 
                    v-if="form.photo" 
                    :src="getPhotoUrl(formPhoto)" 
                    :alt="formNames"
                    class="w-full h-full object-cover"
                    @error="(e: Event) => (e.target as HTMLImageElement).src = ''"
                  />
                  <div 
                    v-else 
                    class="flex h-full w-full items-center justify-center bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-theme-sm"
                  >
                    Sin foto
                  </div>
                </div>
                
                <!-- Camera for new photo -->
                <div v-else class="relative w-48 h-48 rounded-full overflow-hidden border-2 border-gray-300 dark:border-gray-600 bg-gray-100">
                  <video ref="videoRef" autoplay playsinline class="w-full h-full object-cover"></video>
                  <canvas ref="canvasRef" class="hidden"></canvas>
                </div>
                
                <div class="flex gap-2">
                  <button
                    v-if="!showCamera"
                    @click="toggleCamera"
                    type="button"
                    class="rounded-lg bg-brand-500 px-4 py-2 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                  >
                    {{ formPhoto ? 'Actualizar Foto' : 'Tomar Foto' }}
                  </button>
                  <button
                    v-if="showCamera"
                    @click="takePhoto"
                    type="button"
                    class="rounded-lg bg-green-500 px-4 py-2 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-green-600"
                  >
                    Capturar
                  </button>
                  <button
                    v-if="showCamera"
                    @click="toggleCamera"
                    type="button"
                    class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
                  >
                    Cancelar
                  </button>
                </div>
                
                <p v-if="photoRequired" class="text-sm text-error-500">La foto es obligatoria</p>
                <p v-if="formPhoto && !formPhoto.startsWith('data:') && !showCamera" class="text-sm text-success-500">Foto guardada</p>
                <p v-if="formPhoto && formPhoto.startsWith('data:')" class="text-sm text-yellow-500">Foto nueva lista para subir</p>
              </div>
            </div>

            <!-- Names -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Nombres <span class="text-error-500">*</span>
              </label>
              <input
                v-model="form.names"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                placeholder="Nombres"
              />
            </div>

            <!-- Surnames -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Apellidos <span class="text-error-500">*</span>
              </label>
              <input
                v-model="form.surnames"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                placeholder="Apellidos"
              />
            </div>

            <!-- ID Card Number -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Cédula <span class="text-error-500">*</span>
              </label>
              <input
                v-model="form.id_card_number"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                placeholder="4-711-1234"
              />
            </div>

            <!-- Gender -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Género <span class="text-error-500">*</span>
              </label>
              <Multiselect
                v-model="form.gender"
                :options="genderOptions"
                :searchable="false"
                :close-on-select="true"
                placeholder="Seleccione género"
                label="label"
                track-by="value"
                class="multiselect-dark"
              />
            </div>
            
            <!-- Province -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Provincia
              </label>
              <Multiselect
                v-model="form.province"
                :options="provinceOptions"
                :searchable="true"
                :close-on-select="true"
                placeholder="Seleccione provincia"
                label="label"
                track-by="value"
                class="multiselect-dark"
                @search-change="searchProvince"
              />
            </div>

            <!-- Nationality -->
            <div>
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                Nacionalidad
              </label>
              <input
                v-model="form.nationality"
                type="text"
                class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                placeholder="Nacionalidad"
              />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="closeForm"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cancelar
          </button>
          <button
            @click="saveVisitor"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4" @click.self="closeDelete">
      <div class="w-full max-w-md mx-auto overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="p-6 text-center">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-error-50 dark:bg-error-900/20 mb-4">
            <svg class="w-7 h-7 text-error-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-base font-medium text-gray-900 dark:text-white mb-2">Confirmar eliminación</h3>
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">
            ¿Está seguro que desea eliminar este visitante? Esta acción no se puede deshacer.
          </p>
        </div>
        <div class="flex justify-center gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="closeDelete"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cancelar
          </button>
          <button
            @click="confirmDeleteAction"
            class="rounded-lg bg-error-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-error-600"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
