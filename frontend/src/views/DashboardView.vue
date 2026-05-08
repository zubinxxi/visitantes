<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/lib/api'
import type { VisitStats, Visit } from '@/types/visit'

const PANAMA_TZ = 'America/Panama'

const stats = ref<VisitStats | null>(null)
const recentVisits = ref<Visit[]>([])
const loading = ref(true)

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString('es-PA', { timeZone: PANAMA_TZ, hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-PA', { timeZone: PANAMA_TZ, day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const [statsRes, visitsRes] = await Promise.all([
      api.get('/visits/stats/summary'),
      api.get('/visits/', { params: { limit: 8 } }),
    ])
    stats.value = statsRes.data
    recentVisits.value = visitsRes.data
  } catch (error) {
    console.error('Error al cargar dashboard:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <template v-else>
      <div class="mb-6">
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">Dashboard</h1>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-6">
        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-theme-xs">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">Visitas Totales</p>
              <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{{ stats?.total_visits ?? 0 }}</p>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            </div>
          </div>
          <div class="mt-4 flex items-center text-theme-xs">
            <span class="text-gray-500 dark:text-gray-400">Histórico completo</span>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-theme-xs">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">Activas Ahora</p>
              <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{{ stats?.active_visits ?? 0 }}</p>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-success-50 dark:bg-success-500/10 text-success-500 dark:text-success-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </div>
          </div>
          <div class="mt-4 flex items-center text-theme-xs">
            <span class="text-gray-500 dark:text-gray-400">Actualmente en el edificio</span>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-theme-xs">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">Visitas Hoy</p>
              <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{{ stats?.today_visits ?? 0 }}</p>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-warning-50 dark:bg-warning-500/10 text-warning-500 dark:text-warning-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            </div>
          </div>
          <div class="mt-4 flex items-center text-theme-xs">
            <span class="text-gray-500 dark:text-gray-400">{{ new Date().toLocaleDateString('es-PA', { day: 'numeric', month: 'short' }) }}</span>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-5 shadow-theme-xs">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-theme-sm text-gray-500 dark:text-gray-400">Visitantes Únicos</p>
              <p class="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{{ stats?.unique_visitors ?? 0 }}</p>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-error-50 dark:bg-error-500/10 text-error-500 dark:text-error-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            </div>
          </div>
          <div class="mt-4 flex items-center text-theme-xs">
            <span class="text-gray-500 dark:text-gray-400">Registrados en el sistema</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div class="xl:col-span-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
          <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
            <h3 class="text-base font-medium text-gray-800 dark:text-white">Últimas Visitas</h3>
            <router-link to="/active" class="text-theme-sm font-medium text-brand-500 hover:text-brand-600 dark:hover:text-brand-400">
              Ver todas →
            </router-link>
          </div>

          <div v-if="recentVisits.length === 0" class="py-12 text-center text-gray-500 dark:text-gray-400">
            <svg class="mx-auto mb-4 h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            <p class="text-sm">No hay visitas registradas</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                  <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400">Visitante</th>
                  <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400">Cédula</th>
                  <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400">Fecha</th>
                  <th class="px-6 py-3 text-left text-theme-xs font-medium uppercase text-gray-400">Estado</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                <tr v-for="visit in recentVisits" :key="visit.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="flex h-9 w-9 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 font-semibold text-theme-sm">
                        {{ visit.names?.charAt(0) || '?' }}{{ visit.surnames?.charAt(0) || '' }}
                      </div>
                      <div>
                        <p class="text-theme-sm font-medium text-gray-800 dark:text-white">{{ visit.names }} {{ visit.surnames }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ visit.id_card_number }}</td>
                  <td class="px-6 py-4 text-theme-sm text-gray-500 dark:text-gray-400">{{ formatDate(visit.check_in) }} {{ formatTime(visit.check_in) }}</td>
                  <td class="px-6 py-4">
                    <span
                      :class="[
                        'inline-flex items-center rounded-full px-2.5 py-1 text-theme-xs font-medium',
                        visit.check_out
                          ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                          : 'bg-success-50 dark:bg-success-500/10 text-success-700 dark:text-success-400',
                      ]"
                    >
                      {{ visit.check_out ? 'Finalizada' : 'Activa' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs">
          <div class="border-b border-gray-200 dark:border-gray-800 px-6 py-4">
            <h3 class="text-base font-medium text-gray-800 dark:text-white">Acciones Rápidas</h3>
          </div>
          <div class="p-6 space-y-3">
            <router-link
              to="/checkin"
              class="flex items-center gap-4 rounded-lg border border-gray-200 dark:border-gray-800 p-4 transition-all hover:border-brand-200 dark:hover:border-brand-500/30 hover:bg-brand-50 dark:hover:bg-brand-500/5 group"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-500/10 text-brand-500 dark:text-brand-400 transition-colors group-hover:bg-brand-500 group-hover:text-white">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" /></svg>
              </div>
              <div>
                <p class="text-theme-sm font-medium text-gray-800 dark:text-white">Nuevo Check-In</p>
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">Registrar visitante</p>
              </div>
            </router-link>

            <router-link
              to="/active"
              class="flex items-center gap-4 rounded-lg border border-gray-200 dark:border-gray-800 p-4 transition-all hover:border-success-200 dark:hover:border-success-500/30 hover:bg-success-50 dark:hover:bg-success-500/5 group"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-success-50 dark:bg-success-500/10 text-success-500 dark:text-success-400 transition-colors group-hover:bg-success-500 group-hover:text-white">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              </div>
              <div>
                <p class="text-theme-sm font-medium text-gray-800 dark:text-white">Visitas Activas</p>
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">{{ stats?.active_visits || 0 }} en el edificio</p>
              </div>
            </router-link>

            <router-link
              to="/checkout"
              class="flex items-center gap-4 rounded-lg border border-gray-200 dark:border-gray-800 p-4 transition-all hover:border-error-200 dark:hover:border-error-500/30 hover:bg-error-50 dark:hover:bg-error-500/5 group"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-error-50 dark:bg-error-500/10 text-error-500 dark:text-error-400 transition-colors group-hover:bg-error-500 group-hover:text-white">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 11-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
              </div>
              <div>
                <p class="text-theme-sm font-medium text-gray-800 dark:text-white">Checkout Rápido</p>
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">Salida con QR</p>
              </div>
            </router-link>

            <router-link
              to="/visitors"
              class="flex items-center gap-4 rounded-lg border border-gray-200 dark:border-gray-800 p-4 transition-all hover:border-warning-200 dark:hover:border-warning-500/30 hover:bg-warning-50 dark:hover:bg-warning-500/5 group"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-warning-50 dark:bg-warning-500/10 text-warning-500 dark:text-warning-400 transition-colors group-hover:bg-warning-500 group-hover:text-white">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </div>
              <div>
                <p class="text-theme-sm font-medium text-gray-800 dark:text-white">Buscar Visitante</p>
                <p class="text-theme-xs text-gray-500 dark:text-gray-400">Historial y búsqueda</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
