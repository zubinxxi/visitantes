<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { usePermissionsStore } from '@/stores/permissions'
import { useSidebar } from '@/composables/useSidebar'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()
const perms = usePermissionsStore()
const {
  isCollapsed: sidebarCollapsed,
  isMobileOpen: sidebarOpen,
  toggleCollapse,
  toggleMobile,
  setHovered: setSidebarHovered,
  sidebarExpanded,
} = useSidebar()
const profileOpen = ref(false)
const changePasswordOpen = ref(false)
const cpCurrentPassword = ref('')
const cpNewPassword = ref('')
const cpConfirmPassword = ref('')
const cpLoading = ref(false)
const cpError = ref('')
const cpSuccess = ref('')

const navItems = [
  {
    to: '/',
    label: 'Dashboard',
    appName: 'dashboard',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>`,
  },
  {
    to: '/checkin',
    label: 'Check-In',
    appName: 'checkin',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/></svg>`,
  },
  {
    to: '/active',
    label: 'Visitas Activas',
    appName: 'active_visits',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`,
  },
  {
    to: '/checkout',
    label: 'Checkout Rápido',
    appName: 'checkout',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 11-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>`,
  },
  {
    to: '/visitors',
    label: 'Visitantes',
    appName: 'visitors',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>`,
  },
  {
    to: '/history',
    label: 'Historial',
    appName: 'visit_history',
    icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`,
  },
]

const maintenanceItems = [
  { to: '/maintenance/provinces', label: 'Provincias', appName: 'maint_provinces' },
  { to: '/maintenance/institutions', label: 'Instituciones', appName: 'maint_institutions' },
  { to: '/maintenance/type-uadm', label: 'Tipos de UADM', appName: 'maint_type_uadm' },
  { to: '/maintenance/buildings', label: 'Edificios', appName: 'maint_buildings' },
  { to: '/maintenance/procedures', label: 'Tipo de Trámite', appName: 'maint_procedures' },
  { to: '/maintenance/uadms', label: 'Unidades Administrativas', appName: 'maint_uadms' },
]

const securityItems = [
  { to: '/security/users', label: 'Usuarios', appName: 'sec_users' },
  { to: '/security/groups', label: 'Grupos', appName: 'sec_groups' },
  { to: '/security/apps', label: 'Aplicaciones', appName: 'sec_apps' },
  { to: '/security/permissions', label: 'Permisos por Grupo', appName: 'sec_permissions' },
  { to: '/security/members', label: 'Miembros por Grupo', appName: 'sec_members' },
]

const filteredNavItems = computed(() =>
  navItems.filter((item) => perms.hasAccess(item.appName)),
)

const filteredMaintenanceItems = computed(() => {
  if (!perms.isAdmin) return []
  return maintenanceItems.filter((item) => perms.hasAccess(item.appName))
})

const filteredSecurityItems = computed(() => {
  return securityItems.filter((item) => perms.hasAccess(item.appName))
})

onMounted(() => {
  if (perms.permissions.length === 0 && localStorage.getItem('token')) {
    perms.refreshPermissions()
  }
})

const allRoutes = [
  ...navItems,
  ...maintenanceItems.map((item) => ({ to: item.to, label: item.label, icon: '' })),
  ...securityItems.map((item) => ({ to: item.to, label: item.label, icon: '' })),
]

const currentTitle = computed(() => {
  const item = allRoutes.find((n) => n.to === route.path)
  return item ? item.label : 'Dashboard'
})

function isActive(path: string) {
  return route.path === path
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

async function handleChangePassword() {
  if (cpNewPassword.value !== cpConfirmPassword.value) {
    cpError.value = 'Las contraseñas no coinciden'
    return
  }
  if (cpNewPassword.value.length < 6) {
    cpError.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }

  cpLoading.value = true
  cpError.value = ''
  cpSuccess.value = ''
  try {
    await auth.changePassword(cpCurrentPassword.value, cpNewPassword.value)
    cpSuccess.value = 'Contraseña actualizada exitosamente'
    cpCurrentPassword.value = ''
    cpNewPassword.value = ''
    cpConfirmPassword.value = ''
    setTimeout(() => {
      changePasswordOpen.value = false
      cpSuccess.value = ''
    }, 2000)
  } catch (e: unknown) {
    cpError.value = e instanceof Error ? e.message : 'Error al cambiar la contraseña'
  } finally {
    cpLoading.value = false
  }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900" @click="profileOpen = false">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      @click="toggleMobile()"
      class="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 z-50 flex h-screen flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300 ease-in-out',
        sidebarExpanded() ? 'lg:w-[290px]' : 'lg:w-[90px]',
        sidebarOpen ? 'translate-x-0 w-[290px]' : '-translate-x-full lg:translate-x-0',
      ]"
      @mouseenter="setSidebarHovered(true)"
      @mouseleave="setSidebarHovered(false)"
    >
      <!-- Logo -->
      <div class="flex h-16 items-center justify-between border-b border-gray-200 dark:border-gray-800 px-4">
        <router-link to="/" :class="['flex', sidebarExpanded() ? 'items-center' : 'items-center justify-center w-full']">
          <div :class="['flex items-center rounded-lg bg-brand-500', sidebarExpanded() ? 'h-10 px-3 gap-2' : 'h-9 w-9 p-1.5 justify-center']">
            <img src="/img/logo-amo-blanco.png" alt="Logo" :class="sidebarExpanded() ? 'h-6 w-auto' : 'w-full h-full object-contain'" />
            <span v-show="sidebarExpanded()" class="text-white font-semibold text-sm whitespace-nowrap">VisitantesDB</span>
          </div>
        </router-link>
        <button
          @click="toggleCollapse"
          class="hidden lg:flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/5"
        >
          <svg
            :class="['w-5 h-5 transition-transform duration-300', sidebarCollapsed ? 'rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto px-5 py-6">
        <h2
          :class="[
            'mb-4 text-xs font-medium uppercase leading-5 text-gray-400 dark:text-gray-500',
            sidebarExpanded() ? '' : 'lg:text-center',
          ]"
        >
          {{ sidebarExpanded() ? 'Menú Principal' : '•••' }}
        </h2>

        <ul class="flex flex-col gap-4">
          <li v-for="item in filteredNavItems" :key="item.to">
            <router-link
              :to="item.to"
              :class="[
                'menu-item group',
                isActive(item.to) ? 'menu-item-active' : 'menu-item-inactive',
                sidebarExpanded() ? 'lg:justify-start' : 'lg:justify-center',
              ]"
            >
              <span :class="isActive(item.to) ? 'menu-item-icon-active' : 'menu-item-icon-inactive'">
                <span v-html="item.icon"></span>
              </span>
              <span v-show="sidebarExpanded()" class="text-theme-sm">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>

        <!-- Maintenance menu -->
        <div v-if="filteredMaintenanceItems.length > 0" v-show="sidebarExpanded()" class="mt-6">
          <h2 class="mb-4 text-xs font-medium uppercase leading-5 text-gray-400 dark:text-gray-500">
            Mantenimiento
          </h2>
          <ul class="flex flex-col gap-1">
            <li v-for="item in filteredMaintenanceItems" :key="item.to">
              <router-link
                :to="item.to"
                :class="[
                  'menu-item pl-9 group',
                  isActive(item.to) ? 'menu-item-active' : 'menu-item-inactive',
                ]"
              >
                <span class="w-1.5 h-1.5 rounded-full mr-2" :class="isActive(item.to) ? 'bg-brand-500 dark:bg-brand-400' : 'bg-gray-300 dark:bg-gray-600'"></span>
                <span class="text-theme-sm">{{ item.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Security menu -->
        <div v-if="filteredSecurityItems.length > 0" v-show="sidebarExpanded()" class="mt-6">
          <h2 class="mb-4 text-xs font-medium uppercase leading-5 text-gray-400 dark:text-gray-500">
            Seguridad
          </h2>
          <ul class="flex flex-col gap-1">
            <li v-for="item in filteredSecurityItems" :key="item.to">
              <router-link
                :to="item.to"
                :class="[
                  'menu-item pl-9 group',
                  isActive(item.to) ? 'menu-item-active' : 'menu-item-inactive',
                ]"
              >
                <span class="w-1.5 h-1.5 rounded-full mr-2" :class="isActive(item.to) ? 'bg-brand-500 dark:bg-brand-400' : 'bg-gray-300 dark:bg-gray-600'"></span>
                <span class="text-theme-sm">{{ item.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <!-- User footer -->
      <div class="border-t border-gray-200 dark:border-gray-800 p-4">
        <div :class="['flex flex-col gap-3', sidebarExpanded() ? '' : 'lg:items-center']">
          <div :class="['flex items-center gap-3', sidebarExpanded() ? '' : 'lg:justify-center']">
            <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-brand-500 text-white font-semibold text-sm">
              {{ auth.user?.name?.charAt(0) || 'U' }}
            </div>
            <div v-show="sidebarExpanded()" class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-gray-900 dark:text-white">{{ auth.user?.name || 'Usuario' }}</p>
              <p class="truncate text-xs text-gray-500 dark:text-gray-400">{{ auth.user?.email || auth.user?.login }}</p>
            </div>
          </div>
          <button
            @click="handleLogout"
            :class="[
              'flex items-center justify-center gap-2 rounded-lg border border-error-200 dark:border-error-800 bg-error-50 dark:bg-error-900/20 px-3 py-2 text-theme-xs font-medium text-error-600 dark:text-error-400 shadow-theme-xs hover:bg-error-100 dark:hover:bg-error-900/30 transition-colors w-full',
              sidebarExpanded() ? '' : 'lg:px-2',
            ]"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span v-show="sidebarExpanded()">Salir</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content area -->
    <div class="flex flex-1 flex-col transition-all duration-300" :class="sidebarExpanded() ? 'lg:ml-[290px]' : 'lg:ml-[90px]'">
      <!-- Header -->
      <header class="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 sm:px-6">
        <div class="flex items-center gap-4">
          <button @click="toggleMobile()" class="lg:hidden rounded-lg p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/5">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <nav class="hidden sm:flex items-center gap-2 text-sm">
            <router-link to="/" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">Dashboard</router-link>
            <span class="text-gray-300 dark:text-gray-600">/</span>
            <span class="font-medium text-gray-800 dark:text-white">{{ currentTitle }}</span>
          </nav>
        </div>

        <div class="flex items-center gap-3">
          <span class="hidden text-sm text-gray-500 dark:text-gray-400 md:block">
            {{ new Date().toLocaleDateString('es-PA', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }) }}
          </span>

          <!-- Theme toggle -->
          <button
            @click="themeStore.toggleTheme"
            class="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/5 transition-colors"
            :title="themeStore.isDarkMode ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
          >
            <svg v-if="!themeStore.isDarkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </button>

          <!-- User profile dropdown -->
          <div class="relative" @click.stop>
            <button
              @click="profileOpen = !profileOpen"
              class="flex items-center gap-2 pl-3 border-l border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-white/5 rounded-lg py-1.5 px-2 transition-colors"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500 text-white font-semibold text-xs">
                {{ auth.user?.name?.charAt(0) || 'U' }}
              </div>
              <span class="hidden text-sm font-medium text-gray-700 dark:text-gray-200 md:block">
                {{ auth.user?.name || 'Usuario' }}
              </span>
              <svg class="w-4 h-4 text-gray-400" :class="{ 'rotate-180': profileOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <div
              v-if="profileOpen"
              class="absolute right-0 mt-2 w-56 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-md overflow-hidden z-50"
            >
              <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-800">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ auth.user?.name || 'Usuario' }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ auth.user?.email || auth.user?.login }}</p>
              </div>

              <div class="py-1">
                <button
                  @click="changePasswordOpen = true; profileOpen = false"
                  class="flex items-center gap-3 w-full px-4 py-2.5 text-theme-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors text-left"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                  Cambiar contraseña
                </button>
              </div>

              <div v-if="filteredSecurityItems.length > 0" class="py-1 border-t border-gray-200 dark:border-gray-800">
                <p class="px-4 py-2 text-xs font-medium uppercase text-gray-400 dark:text-gray-500">Seguridad</p>
                <router-link
                  v-for="item in filteredSecurityItems"
                  :key="item.to"
                  :to="item.to"
                  @click="profileOpen = false"
                  :class="[
                    'flex items-center gap-3 px-4 py-2.5 text-theme-sm transition-colors',
                    isActive(item.to)
                      ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5',
                  ]"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  {{ item.label }}
                </router-link>
              </div>

              <div class="border-t border-gray-200 dark:border-gray-800 py-1">
                <router-link
                  v-if="perms.hasAccess('config')"
                  to="/config"
                  @click="profileOpen = false"
                  class="flex items-center gap-3 px-4 py-2.5 text-theme-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Configuración
                </router-link>
                <button
                  @click="handleLogout"
                  class="flex items-center gap-3 w-full px-4 py-2.5 text-theme-sm text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/10 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Cerrar sesión
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6">
        <RouterView />
      </main>
    </div>
  </div>

  <!-- Change Password Modal -->
  <div v-if="changePasswordOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/50 backdrop-blur-sm">
    <div class="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-theme-xl overflow-hidden" @click.stop>
      <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Cambiar Contraseña</h3>
        <button @click="changePasswordOpen = false" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="handleChangePassword" class="p-6">
        <div v-if="cpError" class="mb-4 rounded-lg bg-error-50 dark:bg-error-900/20 px-4 py-3 border border-error-200 dark:border-error-800">
          <p class="text-sm text-error-600 dark:text-error-400">{{ cpError }}</p>
        </div>
        <div v-if="cpSuccess" class="mb-4 rounded-lg bg-success-50 dark:bg-success-900/20 px-4 py-3 border border-success-200 dark:border-success-800">
          <p class="text-sm text-success-600 dark:text-success-400">{{ cpSuccess }}</p>
        </div>

        <div class="space-y-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Contraseña Actual</label>
            <input 
              v-model="cpCurrentPassword" 
              type="password" 
              class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-sm dark:text-white focus:border-brand-500 focus:ring-brand-500/10" 
              required
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Nueva Contraseña</label>
            <input 
              v-model="cpNewPassword" 
              type="password" 
              class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-sm dark:text-white focus:border-brand-500 focus:ring-brand-500/10" 
              required
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Confirmar Nueva Contraseña</label>
            <input 
              v-model="cpConfirmPassword" 
              type="password" 
              class="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-sm dark:text-white focus:border-brand-500 focus:ring-brand-500/10" 
              required
            />
          </div>
        </div>

        <div class="mt-8 flex gap-3">
          <button 
            type="button" 
            @click="changePasswordOpen = false" 
            class="flex-1 rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            :disabled="cpLoading"
            class="flex-1 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 flex items-center justify-center"
          >
            <span v-if="cpLoading" class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            Actualizar
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
