<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/lib/api'
import Multiselect from 'vue-multiselect'
import { useToast } from '@/composables/useToast'

const { error: showError, success } = useToast()

const groups = ref<Array<{id: number, name: string}>>([])
const selectedGroup = ref<{id: number, name: string} | null>(null)
const groupUsers = ref<string[]>([])
const apps = ref<Array<{app_name: string, description: string}>>([])
const permissions = ref<Record<string, Record<string, boolean>>>({})
const permissionIds = ref<Record<string, number>>({})

const privileges = [
  { key: 'priv_access', label: 'Acceso' },
  { key: 'priv_insert', label: 'Crear' },
  { key: 'priv_update', label: 'Editar' },
  { key: 'priv_delete', label: 'Borrar' },
  { key: 'priv_export', label: 'Exportar' },
  { key: 'priv_print', label: 'Imprimir' },
]

async function loadGroups() {
  try {
    const res = await api.get('/maintenance/groups', { params: { limit: 100 } })
    groups.value = res.data.items || res.data
  } catch (e) {
    console.error('Error loading groups:', e)
  }
}

async function loadApps() {
  try {
    const res = await api.get('/maintenance/apps', { params: { limit: 100 } })
    apps.value = res.data.items || res.data
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
    const res = await api.get(`/security/groups/${selectedGroup.value.id}/users`)
    groupUsers.value = res.data || []
  } catch (e) {
    console.error('Error loading group users:', e)
    groupUsers.value = []
  }
}

async function loadPermissions() {
  if (!selectedGroup.value) {
    permissions.value = {}
    permissionIds.value = {}
    return
  }
  try {
    const res = await api.get('/maintenance/group_apps', {
      params: { group_id: selectedGroup.value.id }
    })
    const perms: Record<string, Record<string, boolean>> = {}
    const ids: Record<string, number> = {}
    ;(res.data.items || res.data).forEach((p: Record<string, unknown>) => {
      const appName = p.app_name as string
      if (p.id) ids[appName] = p.id as number
      if (!perms[appName]) perms[appName] = {} as Record<string, boolean>
      const appPerms = perms[appName]!
      privileges.forEach(priv => {
        const privValue = p[priv.key] as string
        appPerms[priv.key] = privValue === 'Y'
      })
    })
    permissions.value = perms
    permissionIds.value = ids
  } catch (e) {
    console.error('Error loading permissions:', e)
  }
}

watch(selectedGroup, () => {
  loadGroupUsers()
  loadPermissions()
})

async function togglePermission(appName: string, privKey: string) {
  if (!selectedGroup.value) return
  const current = permissions.value[appName]?.[privKey] || false
  const newVal = !current
  const recordId = permissionIds.value[appName]
  
  try {
    const payload: Record<string, unknown> = {
      group_id: selectedGroup.value.id,
      app_name: appName,
      [privKey]: newVal ? 'Y' : 'N'
    }

    if (recordId) {
      await api.put(`/maintenance/group_apps/${recordId}`, payload)
    } else {
      await api.post('/maintenance/group_apps', payload)
      await loadPermissions()
    }

    if (!permissions.value[appName]) permissions.value[appName] = {}
    permissions.value[appName][privKey] = newVal
    success('Permiso actualizado')
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al actualizar permiso'
    showError(errMsg)
  }
}

function isAdminGroup(): boolean {
  return selectedGroup.value?.name === 'administrador' || selectedGroup.value?.id === 1
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
        label="name"
        track-by="id"
        class="multiselect-dark"
      />
    </div>

    <div v-if="selectedGroup" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
        <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            Usuarios en {{ selectedGroup.name }}
          </h3>
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

      <div class="lg:col-span-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
        <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            Matriz de Permisos - {{ selectedGroup.name }}
          </h3>
          <p v-if="isAdminGroup()" class="text-theme-xs text-gray-500 dark:text-gray-400 mt-1">
            Los administradores tienen todos los permisos por defecto
          </p>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400">Aplicación</th>
                <th v-for="priv in privileges" :key="priv.key" class="px-6 py-3 text-center text-theme-xs font-medium uppercase text-gray-400">
                  {{ priv.label }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
              <tr v-for="app in apps" :key="app.app_name" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-6 py-4 text-theme-sm font-medium text-gray-800 dark:text-white">
                  {{ app.description || app.app_name }}
                </td>
                <td v-for="priv in privileges" :key="priv.key" class="px-6 py-4 text-center">
                  <button
                    @click="togglePermission(app.app_name, priv.key)"
                    :disabled="isAdminGroup()"
                    :class="[
                      'w-6 h-6 rounded border-2 transition-colors',
                      permissions[app.app_name]?.[priv.key]
                        ? 'bg-brand-500 border-brand-500 text-white'
                        : 'border-gray-300 dark:border-gray-600 hover:border-brand-300',
                      isAdminGroup() ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                    ]"
                  >
                    <svg v-if="permissions[app.app_name]?.[priv.key]" class="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
</template>
