<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/lib/api'
import { useToast } from '@/composables/useToast'
import Multiselect from 'vue-multiselect'

const { success, error: showError } = useToast()

interface User {
  login: string
  name: string
  email: string
  role: string
  active: string
  priv_admin: string
  phone: string
}

interface Group {
  group_id: number
  description: string
}

const users = ref<User[]>([])
const groups = ref<Group[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingUser = ref<User | null>(null)
const showDeleteConfirm = ref(false)
const deletingUser = ref<string | null>(null)

const form = ref({
  login: '',
  name: '',
  email: '',
  role: '',
  active: { label: 'Sí', value: 'Y' },
  priv_admin: { label: 'No', value: 'N' },
  phone: '',
  selectedGroups: [] as Group[],
})

const selectOptions: { label: string; value: string }[] = [
  { label: 'Sí', value: 'Y' },
  { label: 'No', value: 'N' },
]

async function loadUsers() {
  loading.value = true
  try {
    const res = await api.get('/maintenance/users', { params: { limit: 200 } })
    users.value = res.data.items || res.data
  } catch (e) {
    console.error('Error loading users:', e)
  } finally {
    loading.value = false
  }
}

async function loadGroups() {
  try {
    const res = await api.get('/maintenance/groups', { params: { limit: 100 } })
    groups.value = res.data.items || res.data
  } catch (e) {
    console.error('Error loading groups:', e)
  }
}

async function loadUserGroups(login: string): Promise<Group[]> {
  try {
    const res = await api.get(`/security/groups?login=${login}`)
    return res.data || []
  } catch {
    return []
  }
}

function getSelectObj(value: string): { label: string; value: string } {
  return selectOptions.find(o => o.value === value) || selectOptions[1]!
}

function openCreate() {
  editingUser.value = null
  form.value = {
    login: '',
    name: '',
    email: '',
    role: '',
    active: getSelectObj('Y'),
    priv_admin: getSelectObj('N'),
    phone: '',
    selectedGroups: [],
  }
  showForm.value = true
}

async function openEdit(user: User) {
  editingUser.value = user
  const userGroups = await loadUserGroups(user.login)
  form.value = {
    login: user.login,
    name: user.name || '',
    email: user.email || '',
    role: user.role || '',
    active: getSelectObj(user.active || 'Y'),
    priv_admin: getSelectObj(user.priv_admin || 'N'),
    phone: user.phone || '',
    selectedGroups: userGroups,
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingUser.value = null
}

async function saveUser() {
  try {
    const payload = {
      login: form.value.login,
      name: form.value.name,
      email: form.value.email,
      role: form.value.role,
      active: form.value.active?.value || 'Y',
      priv_admin: form.value.priv_admin?.value || 'N',
      phone: form.value.phone,
    }

    if (editingUser.value) {
      await api.put(`/maintenance/users/${form.value.login}`, payload)
      const currentGroups = form.value.selectedGroups.map(g => g.group_id)
      const allGroups = groups.value.map(g => g.group_id)
      for (const gid of allGroups) {
        if (currentGroups.includes(gid)) {
          await api.post(`/security/groups/${gid}/users/${form.value.login}`).catch(() => {})
        } else {
          await api.delete(`/security/groups/${gid}/users/${form.value.login}`).catch(() => {})
        }
      }
      success('Usuario actualizado correctamente')
    } else {
      await api.post('/maintenance/users', payload)
      for (const g of form.value.selectedGroups) {
        await api.post(`/security/groups/${g.group_id}/users/${form.value.login}`).catch(() => {})
      }
      success('Usuario creado correctamente')
    }
    closeForm()
    await loadUsers()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al guardar'
    showError(errMsg)
  }
}

function confirmDelete(user: User) {
  deletingUser.value = user.login
  showDeleteConfirm.value = true
}

function closeDelete() {
  showDeleteConfirm.value = false
  deletingUser.value = null
}

async function deleteUser() {
  if (!deletingUser.value) return
  try {
    await api.delete(`/maintenance/users/${deletingUser.value}`)
    success('Usuario eliminado correctamente')
    closeDelete()
    await loadUsers()
  } catch (e: unknown) {
    const errMsg = e instanceof Error ? e.message : 'Error al eliminar'
    showError(errMsg)
  }
}

onMounted(() => {
  loadUsers()
  loadGroups()
})
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Usuarios</h1>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ users.length }} registros</p>
      </div>
      <button
        @click="openCreate"
        class="h-10 rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
      >
        Nuevo Usuario
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div
      v-else-if="users.length === 0"
      class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center"
    >
      <p class="text-gray-500 dark:text-gray-400">No hay usuarios registrados</p>
    </div>

    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Login</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Nombre</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Email</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Rol</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Activo</th>
              <th class="px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400">Priv. Admin</th>
              <th class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400 w-24">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="user in users" :key="user.login" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td class="px-6 py-4 text-theme-sm font-medium text-gray-800 dark:text-white">{{ user.login }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-700 dark:text-gray-300">{{ user.name }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ user.email || '-' }}</td>
              <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ user.role || '-' }}</td>
              <td class="px-6 py-4">
                <span v-if="user.active === 'Y'" class="text-success-600 dark:text-success-400">
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
              <td class="px-6 py-4">
                <span v-if="user.priv_admin === 'Y'" class="text-success-600 dark:text-success-400">
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
              <td class="px-6 py-4 text-right">
                <div class="inline-flex gap-1 justify-end">
                  <button
                    @click="openEdit(user)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    title="Editar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="confirmDelete(user)"
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
            {{ editingUser ? 'Editar Usuario' : 'Nuevo Usuario' }}
          </h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 max-h-96 overflow-y-auto space-y-4">
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Login <span class="text-error-500">*</span></label>
            <input
              v-model="form.login"
              type="text"
              :disabled="!!editingUser"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Nombre</label>
            <input
              v-model="form.name"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
            <input
              v-model="form.email"
              type="email"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Rol</label>
            <input
              v-model="form.role"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Teléfono</label>
            <input
              v-model="form.phone"
              type="text"
              class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Activo</label>
            <Multiselect
              v-model="form.active"
              :options="selectOptions"
              :searchable="false"
              :close-on-select="true"
              label="label"
              track-by="value"
              class="multiselect-dark"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Priv. Admin</label>
            <Multiselect
              v-model="form.priv_admin"
              :options="selectOptions"
              :searchable="false"
              :close-on-select="true"
              label="label"
              track-by="value"
              class="multiselect-dark"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">Grupos</label>
            <Multiselect
              v-model="form.selectedGroups"
              :options="groups"
              :multiple="true"
              :close-on-select="true"
              placeholder="Seleccione grupos..."
              label="description"
              track-by="group_id"
              class="multiselect-dark"
            />
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
            @click="saveUser"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
          >
            Guardar
          </button>
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
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">¿Está seguro que desea eliminar este usuario?</p>
        </div>
        <div class="flex justify-center gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="closeDelete"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cancelar
          </button>
          <button
            @click="deleteUser"
            class="rounded-lg bg-error-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-error-600"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
