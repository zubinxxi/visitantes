import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePermissionsStore } from '@/stores/permissions'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('@/views/LayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { appName: 'dashboard' },
        },
        {
          path: 'checkin',
          name: 'checkin',
          component: () => import('@/views/CheckInView.vue'),
          meta: { appName: 'checkin' },
        },
        {
          path: 'active',
          name: 'active',
          component: () => import('@/views/ActiveVisitsView.vue'),
          meta: { appName: 'active_visits' },
        },
        {
          path: 'visitors',
          name: 'visitors',
          component: () => import('@/views/VisitorsView.vue'),
          meta: { appName: 'visitors' },
        },
        {
          path: 'checkout',
          name: 'checkout',
          component: () => import('@/views/CheckoutView.vue'),
          meta: { appName: 'checkout' },
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('@/views/VisitHistoryView.vue'),
          meta: { appName: 'visit_history' },
        },
        {
          path: 'maintenance/provinces',
          name: 'maintenance-provinces',
          component: () => import('@/views/maintenance/ProvincesMaintenance.vue'),
          meta: { appName: 'maint_provinces' },
        },
        {
          path: 'maintenance/institutions',
          name: 'maintenance-institutions',
          component: () => import('@/views/maintenance/InstitutionsMaintenance.vue'),
          meta: { appName: 'maint_institutions' },
        },
        {
          path: 'maintenance/type-uadm',
          name: 'maintenance-type-uadm',
          component: () => import('@/views/maintenance/TypeUadmMaintenance.vue'),
          meta: { appName: 'maint_type_uadm' },
        },
        {
          path: 'maintenance/buildings',
          name: 'maintenance-buildings',
          component: () => import('@/views/maintenance/BuildingMaintenance.vue'),
          meta: { appName: 'maint_buildings' },
        },
        {
          path: 'maintenance/procedures',
          name: 'maintenance-procedures',
          component: () => import('@/views/maintenance/TypeOfProcedureMaintenance.vue'),
          meta: { appName: 'maint_procedures' },
        },
        {
          path: 'maintenance/uadms',
          name: 'maintenance-uadms',
          component: () => import('@/views/maintenance/UadmMaintenance.vue'),
          meta: { appName: 'maint_uadms' },
        },
        {
          path: 'security/users',
          name: 'security-users',
          component: () => import('@/views/maintenance/UsersMaintenance.vue'),
          meta: { appName: 'sec_users' },
        },
        {
          path: 'security/groups',
          name: 'security-groups',
          component: () => import('@/views/maintenance/GroupsMaintenance.vue'),
          meta: { appName: 'sec_groups' },
        },
        {
          path: 'security/apps',
          name: 'security-apps',
          component: () => import('@/views/maintenance/AppsMaintenance.vue'),
          meta: { appName: 'sec_apps' },
        },
        {
          path: 'security/permissions',
          name: 'security-permissions',
          component: () => import('@/views/security/GroupPermissionsView.vue'),
          meta: { appName: 'sec_permissions' },
        },
        {
          path: 'security/members',
          name: 'security-members',
          component: () => import('@/views/security/GroupMembersView.vue'),
          meta: { appName: 'sec_members' },
        },
        {
          path: 'config',
          name: 'config',
          component: () => import('@/views/ConfigView.vue'),
          meta: { appName: 'config' },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const perms = usePermissionsStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { path: '/' }
  }

  const appName = to.meta.appName as string | undefined
  if (appName && auth.isAuthenticated) {
    if (perms.isAdmin) return

    if (perms.permissions.length === 0 && localStorage.getItem('token')) {
      await perms.refreshPermissions()
    }

    if (!perms.hasAccess(appName)) {
      return { path: '/' }
    }
  }
})

export default router
