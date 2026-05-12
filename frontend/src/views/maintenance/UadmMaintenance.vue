<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/lib/api'
import { useToast } from '@/composables/useToast'
import Multiselect from 'vue-multiselect'
import { usePermissionsStore } from '@/stores/permissions'

const perms = usePermissionsStore()

const { success, error: showError } = useToast()

interface Uadm {
  id: number
  name: string
  initials: string
  id_institution: number | null
  id_province: number | null
  id_district: number | null
  id_district_subdivision: number | null
  id_type_uadm: number | null
  id_uadm_origin: number | null
  status: boolean
  province_name?: string
  institution_name?: string
  type_uadm_name?: string
}

interface CatalogItem {
  id: number
  description?: string
  name?: string
}

const uadms = ref<Uadm[]>([])
const loading = ref(true)
const showForm = ref(false)
const editingItem = ref<Uadm | null>(null)
const showDeleteConfirm = ref(false)
const deletingItem = ref<Uadm | null>(null)

const institutions = ref<CatalogItem[]>([])
const provinces = ref<CatalogItem[]>([])
const typeUadms = ref<CatalogItem[]>([])
const uadmOrigins = ref<CatalogItem[]>([])

const form = ref<Record<string, unknown>>({
  name: '',
  initials: '',
  id_institution: null,
  id_province: null,
  id_type_uadm: null,
  id_uadm_origin: null,
  status: null,
})

const statusOptions: { label: string; value: boolean }[] = [
  { label: 'Activo', value: true },
  { label: 'Inactivo', value: false },
]

async function loadUadms() {
  loading.value = true
  try {
    const res = await api.get('/maintenance/uadms/', { params: { limit: 200 } })
    uadms.value = res.data.items || res.data
  } catch (e) {
    console.error('Error loading uadms:', e)
  } finally {
    loading.value = false
  }
}

async function loadCatalogs() {
  try {
    const [instRes, provRes, typeRes, originRes] = await Promise.all([
      api.get('/maintenance/institutions/', { params: { limit: 100 } }),
      api.get('/maintenance/provinces/', { params: { limit: 100 } }),
      api.get('/maintenance/type_uadms/', { params: { limit: 100 } }),
      api.get('/maintenance/uadms/', { params: { limit: 100 } }),
    ])
    institutions.value = instRes.data.items || instRes.data
    provinces.value = provRes.data.items || provRes.data
    typeUadms.value = typeRes.data.items || typeRes.data
    uadmOrigins.value = originRes.data.items || originRes.data
  } catch (e) {
    console.error('Error loading catalogs:', e)
  }
}

function findInCatalog(list: CatalogItem[], id: number | null): CatalogItem | null {
  if (!id) return null
  return list.find(i => i.id === id) || null
}

function getStatusObj(value: boolean): { label: string; value: boolean } {
  return statusOptions.find(s => s.value === value) || statusOptions[0]!
}

function openCreate() {
  editingItem.value = null
  form.value = {
    name: '',
    initials: '',
    id_institution: null,
    id_province: null,
    id_type_uadm: null,
    id_uadm_origin: null,
    status: getStatusObj(true),
  }
  showForm.value = true
}

function openEdit(item: Uadm) {
  editingItem.value = item
  form.value = {
    name: item.name || '',
    initials: item.initials || '',
    id_institution: findInCatalog(institutions.value, item.id_institution),
    id_province: findInCatalog(provinces.value, item.id_province),
    id_type_uadm: findInCatalog(typeUadms.value, item.id_type_uadm),
    id_uadm_origin: findInCatalog(uadmOrigins.value, item.id_uadm_origin),
    status: getStatusObj(!!item.status),
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingItem.value = null
}

async function saveItem() {
  try {
    const statusObj = form.value.status as { value: boolean } | null
    const payload: Record<string, unknown> = {
      name: form.value.name as string || '',
      initials: form.value.initials as string || '',
      id_institution: (form.value.id_institution as CatalogItem | null)?.id || null,
      id_province: (form.value.id_province as CatalogItem | null)?.id || null,
      id_type_uadm: (form.value.id_type_uadm as CatalogItem | null)?.id || null,
      id_uadm_origin: (form.value.id_uadm_origin as CatalogItem | null)?.id || null,
      status: statusObj?.value ?? true,
    }

    if (editingItem.value) {
      await api.put(`/maintenance/uadms/${editingItem.value.id}`, payload)
      success('UADM actualizada correctamente')
    } else {
      await api.post('/maintenance/uadms/', payload)
      success('UADM creada correctamente')
    }
    closeForm()
    await loadUadms()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al guardar'
    showError(errMsg)
  }
}

function confirmDelete(item: Uadm) {
  deletingItem.value = item
  showDeleteConfirm.value = true
}

function closeDelete() {
  showDeleteConfirm.value = false
  deletingItem.value = null
}

async function deleteItem() {
  if (!deletingItem.value) return
  try {
    await api.delete(`/maintenance/uadms/${deletingItem.value.id}`)
    success('UADM eliminada correctamente')
    closeDelete()
    await loadUadms()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al eliminar'
    showError(errMsg)
  }
}

onMounted(() => {
  loadUadms()
  loadCatalogs()
})
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Unidades Administrativas</h1>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ uadms.length }} registros</p>
      </div>
      <button
        v-if="perms.canCreate('maint_uadms')"
        @click="openCreate"
        class="h-10 rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
      >
        Nueva UADM
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div v-else-if="uadms.length === 0" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center">
      <p class="text-gray-500 dark:text-gray-400">No hay unidades administrativas</p>
    </div>

    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Nombre</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Iniciales</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Provincia</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Institución</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Tipo UADM</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Estado</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400 w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="item in uadms" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-6 py-4 text-theme-sm font-medium text-gray-800 dark:text-white">{{ item.name }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.initials || '-' }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.province_name || '-' }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.institution_name || '-' }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.type_uadm_name || '-' }}</td>
              <td class="px-6 py-4">
                <span v-if="item.status" class="text-success-600 dark:text-success-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </span>
                <span v-else class="text-gray-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                  </svg>
                </span>
              </td>
              <td v-if="perms.canEdit('maint_uadms') || perms.canDelete('maint_uadms')" class="px-6 py-4 text-right">
                <div class="inline-flex gap-1 justify-end">
                  <button
                    v-if="perms.canEdit('maint_uadms')"
                    @click="openEdit(item)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    title="Editar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    v-if="perms.canDelete('maint_uadms')"
                    @click="confirmDelete(item)"
                    class="rounded-lg p-2 text-error-500 hover:bg-error-50 dark:hover:bg-error-900/20 transition-colors"
                    title="Eliminar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1H6a1 1 0 00-1 1v7M8 4V3" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4" @click.self="closeForm">
      <div class="w-full max-w-lg mx-auto overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            {{ editingItem ? 'Editar UADM' : 'Nueva UADM' }}
          </h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 max-h-96 overflow-y-auto space-y-4">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Nombre <span class="text-error-500">*</span></label>
            <input v-model="form.name" type="text" class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Iniciales</label>
            <input v-model="form.initials" type="text" class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Institución</label>
            <Multiselect v-model="form.id_institution" :options="institutions" :searchable="true" :close-on-select="true" placeholder="Seleccione..." label="description" track-by="id" class="multiselect-dark" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Provincia</label>
            <Multiselect v-model="form.id_province" :options="provinces" :searchable="true" :close-on-select="true" placeholder="Seleccione..." label="description" track-by="id" class="multiselect-dark" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Tipo UADM</label>
            <Multiselect v-model="form.id_type_uadm" :options="typeUadms" :searchable="true" :close-on-select="true" placeholder="Seleccione..." label="description" track-by="id" class="multiselect-dark" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">UADM Origen</label>
            <Multiselect v-model="form.id_uadm_origin" :options="uadmOrigins" :searchable="true" :close-on-select="true" placeholder="Seleccione..." label="name" track-by="id" class="multiselect-dark" />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Estado</label>
            <Multiselect v-model="form.status" :options="statusOptions" :searchable="false" :close-on-select="true" label="label" track-by="value" class="multiselect-dark" />
          </div>
        </div>
        <div class="flex justify-end gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button @click="closeForm" class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750">Cancelar</button>
          <button @click="saveItem" class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600">Guardar</button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4" @click.self="closeDelete">
      <div class="w-full max-w-md mx-auto overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="p-6 text-center">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-error-50 dark:bg-error-900/20 mb-4">
            <svg class="w-7 h-7 text-error-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-base font-medium text-gray-900 dark:text-white mb-2">Confirmar eliminación</h3>
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">¿Está seguro que desea eliminar esta UADM?</p>
        </div>
        <div class="flex justify-center gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button @click="closeDelete" class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750">Cancelar</button>
          <button @click="deleteItem" class="rounded-lg bg-error-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-error-600">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>
