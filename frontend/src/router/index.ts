import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
        },
        {
          path: 'checkin',
          name: 'checkin',
          component: () => import('@/views/CheckInView.vue'),
        },
        {
          path: 'active',
          name: 'active',
          component: () => import('@/views/ActiveVisitsView.vue'),
        },
        {
          path: 'visitors',
          name: 'visitors',
          component: () => import('@/views/VisitorsView.vue'),
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('@/views/VisitHistoryView.vue'),
        },
        {
          path: 'maintenance/provinces',
          name: 'maintenance-provinces',
          component: () => import('@/views/maintenance/ProvincesMaintenance.vue'),
        },
        {
          path: 'maintenance/institutions',
          name: 'maintenance-institutions',
          component: () => import('@/views/maintenance/InstitutionsMaintenance.vue'),
        },
        {
          path: 'maintenance/type-uadm',
          name: 'maintenance-type-uadm',
          component: () => import('@/views/maintenance/TypeUadmMaintenance.vue'),
        },
        {
          path: 'maintenance/buildings',
          name: 'maintenance-buildings',
          component: () => import('@/views/maintenance/BuildingMaintenance.vue'),
        },
        {
          path: 'maintenance/procedures',
          name: 'maintenance-procedures',
          component: () => import('@/views/maintenance/TypeOfProcedureMaintenance.vue'),
        },
        {
          path: 'maintenance/uadms',
          name: 'maintenance-uadms',
          component: () => import('@/views/maintenance/UadmMaintenance.vue'),
        },
        {
          path: 'security/users',
          name: 'security-users',
          component: () => import('@/views/maintenance/UsersMaintenance.vue'),
        },
        {
          path: 'security/groups',
          name: 'security-groups',
          component: () => import('@/views/maintenance/GroupsMaintenance.vue'),
        },
        {
          path: 'security/apps',
          name: 'security-apps',
          component: () => import('@/views/maintenance/AppsMaintenance.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { path: '/' }
  }
})

export default router
