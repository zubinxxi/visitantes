<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/lib/api'
import Multiselect from 'vue-multiselect'

interface Group {
  group_id: number
  description: string
}

const groups = ref<Group[]>([])
const selectedGroup = ref<Group | null>(null)
const groupUsers = ref<string[]>([])
const loading = ref(false)

async function loadGroups() {
  try {
    const res = await api.get('/maintenance/groups/', { params: { limit: 100 } })
    groups.value = (res.data.items || res.data) as Group[]
  } catch (e) {
    console.error('Error cargando grupos:', e)
  }
}

async function loadGroupUsers() {
  if (!selectedGroup.value) {
    groupUsers.value = []
    return
  }
  loading.value = true
  try {
    const res = await api.get(`/security/groups/${selectedGroup.value.group_id}/users`)
    groupUsers.value = res.data || []
  } catch (e) {
    console.error('Error cargando usuarios del grupo:', e)
    groupUsers.value = []
  } finally {
    loading.value = false
  }
}

watch(selectedGroup, () => {
  loadGroupUsers()
})

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-medium text-gray-800 dark:text-white">Miembros por Grupo</h1>
      <p class="text-theme-sm text-gray-500 dark:text-gray-400">
        Visualizar los usuarios que pertenecen a cada grupo del sistema
      </p>
    </div>

    <!-- Selector de grupo -->
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

    <!-- Lista de miembros -->
    <div v-if="selectedGroup" class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
      <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            Usuarios en "{{ selectedGroup.description }}"
          </h3>
          <p class="text-theme-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {{ groupUsers.length }} miembro{{ groupUsers.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <div class="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10">
          <svg class="w-5 h-5 text-brand-500 dark:text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
      </div>

      <div class="p-6">
        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-8">
          <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
        </div>

        <!-- Sin miembros -->
        <div v-else-if="groupUsers.length === 0" class="text-center py-12">
          <svg class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          <p class="text-gray-500 dark:text-gray-400 text-theme-sm">No hay usuarios en este grupo</p>
          <p class="text-gray-400 dark:text-gray-500 text-theme-xs mt-1">
            Puede asignar usuarios desde el formulario de edición de usuario
          </p>
        </div>

        <!-- Lista de miembros -->
        <ul v-else class="space-y-2">
          <li
            v-for="user in groupUsers"
            :key="user"
            class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-sm">
              {{ user.charAt(0).toUpperCase() }}
            </div>
            <div>
              <span class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ user }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Estado inicial -->
    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center">
      <svg class="w-16 h-16 mx-auto text-gray-200 dark:text-gray-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <p class="text-gray-500 dark:text-gray-400">Seleccione un grupo para ver sus miembros</p>
    </div>
  </div>
</template>
