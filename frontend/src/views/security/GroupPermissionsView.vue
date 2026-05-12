<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/lib/api'
import Multiselect from 'vue-multiselect'
import { useToast } from '@/composables/useToast'

const { error: showError, success } = useToast()

interface Group {
  group_id: number
  description: string
}

interface App {
  app_name: string
  app_type: string
  description: string
}

const groups = ref<Group[]>([])
const selectedGroup = ref<Group | null>(null)
const groupUsers = ref<string[]>([])
const apps = ref<App[]>([])
const permissions = ref<Record<string, Record<string, boolean>>>({})
const saving = ref<string | null>(null)

const privileges = [
  { key: 'priv_access', label: 'Acceso' },
  { key: 'priv_insert', label: 'Crear' },
  { key: 'priv_update', label: 'Editar' },
  { key: 'priv_delete', label: 'Borrar' },
  { key: 'priv_export', label: 'Exportar' },
  { key: 'priv_print', label: 'Imprimir' },
]

// Agrupación de apps por categoría
const appCategories = [
  { label: 'Páginas principales', types: ['page'] },
  { label: 'CRUDs / Módulos', types: ['crud', 'module'] },
]

function getAppsByCategory(category: { types: string[] }) {
  return apps.value.filter((a) => category.types.includes(a.app_type || 'page'))
}

async function loadGroups() {
  try {
    const res = await api.get('/maintenance/groups/', { params: { limit: 100 } })
    groups.value = (res.data.items || res.data) as Group[]
  } catch (e) {
    console.error('Error loading groups:', e)
  }
}

async function loadApps() {
  try {
    const res = await api.get('/maintenance/apps/', { params: { limit: 100 } })
    apps.value = (res.data.items || res.data) as App[]
  } catch (e) {
    console.error('Error loading apps:', e)
  }
}

async function loadGroupUsers() {
  if (!selectedGroup.value) {
    groupUsers.value = []
    return
  }
  try {
    const res = await api.get(`/security/groups/${selectedGroup.value.group_id}/users`)
    groupUsers.value = res.data || []
  } catch (e) {
    console.error('Error loading group users:', e)
    groupUsers.value = []
  }
}

async function loadPermissions() {
  if (!selectedGroup.value) {
    permissions.value = {}
    return
  }
  try {
    const res = await api.get('/maintenance/group_apps/', {
      params: { limit: 500 }
    })
    const perms: Record<string, Record<string, boolean>> = {}
    const allPerms = (res.data.items || res.data) as Record<string, unknown>[]

    // Filtrar solo los del grupo seleccionado
    allPerms
      .filter((p) => p.group_id === selectedGroup.value!.group_id)
      .forEach((p) => {
        const appName = p.app_name as string
        if (!perms[appName]) perms[appName] = {}
        const appPerms = perms[appName]!
        privileges.forEach((priv) => {
          appPerms[priv.key] = (p[priv.key] as string) === 'Y'
        })
      })
    permissions.value = perms
  } catch (e) {
    console.error('Error loading permissions:', e)
  }
}

watch(selectedGroup, () => {
  loadGroupUsers()
  loadPermissions()
})

async function togglePermission(appName: string, privKey: string) {
  if (!selectedGroup.value || isAdminGroup()) return
  const current = permissions.value[appName]?.[privKey] || false
  const newVal = !current
  saving.value = `${appName}-${privKey}`

  try {
    const payload: Record<string, unknown> = {
      group_id: selectedGroup.value.group_id,
      app_name: appName,
      [privKey]: newVal ? 'Y' : 'N',
    }

    // Usar el endpoint especializado de upsert que maneja la clave compuesta
    await api.post('/security/permissions/upsert', payload)

    if (!permissions.value[appName]) permissions.value[appName] = {}
    permissions.value[appName]![privKey] = newVal
    success('Permiso actualizado')
  } catch (e: unknown) {
    console.error('Error updating permission:', e)
    showError('Error al actualizar permiso')
  } finally {
    saving.value = null
  }
}

function isAdminGroup(): boolean {
  return selectedGroup.value?.group_id === 1
}

onMounted(() => {
  loadGroups()
  loadApps()
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-medium text-gray-800 dark:text-white">Permisos por Grupos</h1>
      <p class="text-theme-sm text-gray-500 dark:text-gray-400">Gestionar permisos de acceso, creación, edición y más para cada grupo</p>
    </div>

    <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs p-6 mb-6">
      <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
        Seleccionar Grupo
      </label>
      <Multiselect
        v-model="selectedGroup"
        :options="groups"
        :searchable="true"
        :close-on-select="true"
        placeholder="Seleccione un grupo..."
        label="description"
        track-by="group_id"
        class="multiselect-dark"
      />
    </div>

    <div v-if="selectedGroup" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Usuarios del grupo -->
      <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
        <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            Usuarios en {{ selectedGroup.description }}
          </h3>
          <p class="text-theme-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ groupUsers.length }} miembro{{ groupUsers.length !== 1 ? 's' : '' }}</p>
        </div>
        <div class="p-6">
          <div v-if="groupUsers.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No hay usuarios en este grupo
          </div>
          <ul v-else class="space-y-2">
            <li v-for="user in groupUsers" :key="user" class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-sm">
                {{ user.charAt(0).toUpperCase() }}
              </div>
              <span class="text-theme-sm text-gray-800 dark:text-white">{{ user }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Matriz de permisos -->
      <div class="lg:col-span-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
        <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            Matriz de Permisos - {{ selectedGroup.description }}
          </h3>
          <p v-if="isAdminGroup()" class="text-theme-xs text-success-600 dark:text-success-400 mt-1 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Los administradores tienen todos los permisos por defecto
          </p>
        </div>
        <div class="overflow-x-auto">
          <div v-for="category in appCategories" :key="category.label">
            <div v-if="getAppsByCategory(category).length > 0" class="border-b border-gray-100 dark:border-gray-800">
              <div class="px-6 py-2 bg-gray-25 dark:bg-gray-800/30">
                <span class="text-theme-xs font-semibold uppercase text-gray-500 dark:text-gray-400">{{ category.label }}</span>
              </div>
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                    <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400 w-48">Aplicación</th>
                    <th v-for="priv in privileges" :key="priv.key" class="px-4 py-3 text-center text-theme-xs font-medium uppercase text-gray-400">
                      {{ priv.label }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                  <tr v-for="app in getAppsByCategory(category)" :key="app.app_name" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td class="px-6 py-3.5 text-theme-sm font-medium text-gray-800 dark:text-white">
                      {{ app.description || app.app_name }}
                    </td>
                    <td v-for="priv in privileges" :key="priv.key" class="px-4 py-3.5 text-center">
                      <button
                        @click="togglePermission(app.app_name, priv.key)"
                        :disabled="isAdminGroup() || saving === `${app.app_name}-${priv.key}`"
                        :class="[
                          'w-6 h-6 rounded border-2 transition-all duration-200 inline-flex items-center justify-center',
                          (isAdminGroup() || permissions[app.app_name]?.[priv.key])
                            ? 'bg-brand-500 border-brand-500 text-white'
                            : 'border-gray-300 dark:border-gray-600 hover:border-brand-300 dark:hover:border-brand-500',
                          isAdminGroup() ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer',
                          saving === `${app.app_name}-${priv.key}` ? 'animate-pulse' : '',
                        ]"
                      >
                        <svg v-if="isAdminGroup() || permissions[app.app_name]?.[priv.key]" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
