<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/lib/api'
import { useToast } from '@/composables/useToast'

const { success, error: showError } = useToast()

interface ConfigItem {
  key: string
  value: string
  description: string | null
}

const configs = ref<ConfigItem[]>([])
const loading = ref(true)
const showForm = ref(false)
const editingKey = ref<string | null>(null)
const form = ref({
  key: '',
  value: '',
  description: '',
})

async function loadConfigs() {
  loading.value = true
  try {
    const res = await api.get('/config/')
    configs.value = res.data || []
  } catch (e) {
    console.error('Error loading config:', e)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingKey.value = null
  form.value = { key: '', value: '', description: '' }
  showForm.value = true
}

function openEdit(item: ConfigItem) {
  editingKey.value = item.key
  form.value = { key: item.key, value: item.value, description: item.description || '' }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingKey.value = null
}

async function saveConfig() {
  try {
    if (editingKey.value) {
      await api.put(`/config/${editingKey.value}`, {
        value: form.value.value,
        description: form.value.description || null,
      })
      success('Configuración actualizada')
    } else {
      await api.post('/config/', {
        key: form.value.key,
        value: form.value.value,
        description: form.value.description || null,
      })
      success('Configuración creada')
    }
    closeForm()
    loadConfigs()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al guardar'
    showError(errMsg)
  }
}

async function deleteConfig(item: ConfigItem) {
  if (!confirm(`¿Está seguro de eliminar "${item.key}"?`)) return
  try {
    await api.delete(`/config/${item.key}`)
    success('Configuración eliminada')
    loadConfigs()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al eliminar'
    showError(errMsg)
  }
}

onMounted(loadConfigs)
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Configuración del Sistema</h1>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">Gestionar configuraciones generales</p>
      </div>
      <button
        @click="openCreate"
        class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nueva Configuración
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Key</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Value</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Descripción</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400 w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="item in configs" :key="item.key" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-6 py-4 text-theme-sm font-medium text-gray-800 dark:text-white">{{ item.key }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.value }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ item.description || '-' }}</td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    @click="openEdit(item)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                    title="Editar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 111.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteConfig(item)"
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
    </div>

    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm" @click.self="closeForm">
      <div class="w-full max-w-md mx-4 overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            {{ editingKey ? 'Editar Configuración' : 'Nueva Configuración' }}
          </h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Key <span class="text-error-500">*</span>
            </label>
            <input
              v-model="form.key"
              type="text"
              :disabled="!!editingKey"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
              placeholder="Ej: print_size"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Value <span class="text-error-500">*</span>
            </label>
            <input
              v-model="form.value"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
              placeholder="Ej: S"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
              Descripción
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
              placeholder="Descripción de la configuración"
            ></textarea>
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
            @click="saveConfig"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
