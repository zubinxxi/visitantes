import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/lib/api'

export interface Permission {
  group_id: number
  app_name: string
  priv_access: string | null
  priv_insert: string | null
  priv_delete: string | null
  priv_update: string | null
  priv_export: string | null
  priv_print: string | null
}

const STORAGE_KEY_PERMS = 'user_permissions'
const STORAGE_KEY_GROUPS = 'user_group_ids'
const STORAGE_KEY_PRIV_ADMIN = 'user_priv_admin'
const STORAGE_KEY_VERSION = 'permissions_v'

const CURRENT_VERSION = '2'

const ADMIN_GROUP_ID = 1

export const usePermissionsStore = defineStore('permissions', () => {
  const permissions = ref<Permission[]>([])
  const groupIds = ref<number[]>([])
  const privAdmin = ref<string>('N')

  function loadFromStorage() {
    const version = localStorage.getItem(STORAGE_KEY_VERSION)
    if (version !== CURRENT_VERSION) {
      clearStorage()
      return
    }

    try {
      const perms = localStorage.getItem(STORAGE_KEY_PERMS)
      const groups = localStorage.getItem(STORAGE_KEY_GROUPS)
      const admin = localStorage.getItem(STORAGE_KEY_PRIV_ADMIN)

      if (perms && groups && admin) {
        permissions.value = JSON.parse(perms)
        groupIds.value = JSON.parse(groups)
        privAdmin.value = admin
      }
    } catch {
      clearStorage()
    }
  }

  function clearStorage() {
    permissions.value = []
    groupIds.value = []
    privAdmin.value = 'N'
    localStorage.removeItem(STORAGE_KEY_PERMS)
    localStorage.removeItem(STORAGE_KEY_GROUPS)
    localStorage.removeItem(STORAGE_KEY_PRIV_ADMIN)
    localStorage.removeItem(STORAGE_KEY_VERSION)
  }

  const isAdmin = computed(
    () => privAdmin.value === 'Y' || groupIds.value.includes(ADMIN_GROUP_ID),
  )

  function setPermissions(
    perms: Permission[],
    groups: number[],
    admin: string,
  ) {
    permissions.value = perms
    groupIds.value = groups
    privAdmin.value = admin || 'N'
    localStorage.setItem(STORAGE_KEY_PERMS, JSON.stringify(perms))
    localStorage.setItem(STORAGE_KEY_GROUPS, JSON.stringify(groups))
    localStorage.setItem(STORAGE_KEY_PRIV_ADMIN, admin || 'N')
    localStorage.setItem(STORAGE_KEY_VERSION, CURRENT_VERSION)
  }

  function clearPermissions() {
    clearStorage()
  }

  let refreshPromise: Promise<void> | null = null

  async function refreshPermissions() {
    if (refreshPromise) return refreshPromise

    refreshPromise = (async () => {
      try {
        const res = await api.get('/security/me/permissions')
        setPermissions(
          res.data.permissions || [],
          res.data.group_ids || [],
          res.data.priv_admin || 'N',
        )
      } catch (error: any) {
        console.error('Error refreshing permissions:', error)
        if (error.response?.status === 401) {
          clearPermissions()
        }
      } finally {
        refreshPromise = null
      }
    })()

    return refreshPromise
  }

  function _hasPrivilege(appName: string, privilege: keyof Permission): boolean {
    if (isAdmin.value) return true

    return permissions.value.some(
      (p) => p.app_name === appName && p[privilege] === 'Y',
    )
  }

  function hasAccess(appName: string): boolean {
    if (isAdmin.value) return true

    // Si no hay permisos cargados, asumimos que no tiene acceso hasta que se refresquen.
    // El refresco debe ser manejado por los guardias del router o explícitamente en componentes.
    if (permissions.value.length === 0) {
      return false
    }

    return _hasPrivilege(appName, 'priv_access')
  }

  function canCreate(appName: string): boolean {
    return _hasPrivilege(appName, 'priv_insert')
  }

  function canEdit(appName: string): boolean {
    return _hasPrivilege(appName, 'priv_update')
  }

  function canDelete(appName: string): boolean {
    return _hasPrivilege(appName, 'priv_delete')
  }

  function canExport(appName: string): boolean {
    return _hasPrivilege(appName, 'priv_export')
  }

  function canPrint(appName: string): boolean {
    return _hasPrivilege(appName, 'priv_print')
  }

  loadFromStorage()

  return {
    permissions,
    groupIds,
    privAdmin,
    isAdmin,
    setPermissions,
    clearPermissions,
    refreshPermissions,
    hasAccess,
    canCreate,
    canEdit,
    canDelete,
    canExport,
    canPrint,
  }
})
