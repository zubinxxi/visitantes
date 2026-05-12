# Módulo de Seguridad - Permisos por Grupos de Usuarios

> **ESTADO: COMPLETADO** — Todas las tareas del plan fueron implementadas.

## Contexto

El sistema ya cuenta con la estructura de tablas de seguridad (`sec_groups`, `sec_apps`, `sec_groups_apps`, `sec_users`, `sec_users_groups`) y un mecanismo básico de permisos (`require_permission` en `deps.py`). Sin embargo, actualmente:

1. Las `sec_apps` están definidas a nivel de módulo genérico (`dashboard`, `visitors`, `visits`, `maintenance`, etc.) — no a nivel de página/CRUD individual.
2. El frontend no filtra menús ni rutas según los permisos del usuario.
3. No hay una página dedicada para ver miembros por grupo.
4. Los permisos no se aplican de forma granular (acceso, crear, editar, borrar, imprimir, exportar) por cada página.

### Datos actuales en la BD

**Grupos existentes:**
| group_id | description |
|----------|-------------|
| 1 | Administrador |
| 2 | Usuarios |
| 3 | Seguridad |
| 4 | Admin-Seguridad |

**Apps actuales (pocas, genéricas):**
`dashboard`, `maintenance`, `reports`, `settings`, `visitors`, `visits`

## User Review Required

> [!IMPORTANT]
> **Granularidad de apps**: Se crearán registros en `sec_apps` para cada página/CRUD del sistema (ej: `checkin`, `checkout`, `active_visits`, `visit_history`, `maint_provinces`, `maint_buildings`, `sec_users`, `sec_groups`, `sec_group_permissions`, `sec_group_members`, etc.) en lugar de los módulos genéricos actuales. Esto permite control fino por cada pantalla. Las apps existentes se mantendrán como referencia pero se agregarán las nuevas.

> [!WARNING]
> **Restricción Admin-Seguridad sobre administradores**: El grupo Admin-Seguridad podrá CRUD de usuarios excepto los del grupo Administrador. Esto requiere validación en el backend al crear/editar/borrar usuarios.

## Decisiones de diseño

1. **Grupo Administrador tiene permisos implícitos** (todos los accesos sin necesidad de registros en `sec_groups_apps`). El código actual en `deps.py` ya lo hace con `priv_admin == "Y"`. Se mantiene eso y además se checa si el usuario pertenece al grupo 1 (Administrador).
2. **Datos seed via migración Alembic** para mantener consistencia.
3. **La página "Miembros por Grupo" es solo de visualización**, ya que la asociación de usuarios a grupos se hace en el formulario de creación/edición de usuario mediante un select múltiple existente.

## Proposed Changes

### Componente 1: Nuevas apps en `sec_apps` (Base de datos)

Se insertarán las siguientes apps para tener granularidad a nivel de página:

| app_name | app_type | description |
|----------|----------|-------------|
| `dashboard` | page | Panel principal |
| `profile` | page | Editar perfil |
| `visitors` | crud | Gestión de visitantes |
| `checkin` | page | Registro de visitas (Check-in) |
| `checkout` | page | Checkout rápido |
| `active_visits` | page | Visitas activas |
| `visit_history` | page | Historial de visitas |
| `maint_provinces` | crud | Mantenimiento: Provincias |
| `maint_institutions` | crud | Mantenimiento: Instituciones |
| `maint_type_uadm` | crud | Mantenimiento: Tipos de UADM |
| `maint_buildings` | crud | Mantenimiento: Edificios |
| `maint_procedures` | crud | Mantenimiento: Tipo de trámite |
| `maint_uadms` | crud | Mantenimiento: Unidades Administrativas |
| `sec_users` | crud | Seguridad: Usuarios |
| `sec_groups` | crud | Seguridad: Grupos |
| `sec_apps` | crud | Seguridad: Aplicaciones |
| `sec_permissions` | page | Seguridad: Permisos por grupo |
| `sec_members` | page | Seguridad: Miembros por grupo |
| `config` | page | Configuración del sistema |

#### Permisos por grupo predeterminados:

**Grupo 1 - Administrador:** Todos los permisos (implícito por `priv_admin` + grupo_id=1)

**Grupo 2 - Usuarios:**
- `dashboard`: acceso ✓
- `profile`: acceso ✓, editar ✓

**Grupo 3 - Seguridad:**
- `dashboard`: acceso ✓
- `visitors`: acceso ✓, crear ✓, editar ✓, borrar ✓
- `checkin`: acceso ✓, crear ✓
- `checkout`: acceso ✓, editar ✓
- `active_visits`: acceso ✓
- `visit_history`: acceso ✓

**Grupo 4 - Admin-Seguridad:** Todo lo de Seguridad más:
- `sec_users`: acceso ✓, crear ✓, editar ✓, borrar ✓ (excepto miembros de Administrador)

#### [NEW] Migración Alembic para seed de apps y permisos

Archivo de migración con INSERT de las nuevas apps y permisos predeterminados.

---

### Componente 2: Backend — Nuevo endpoint de permisos del usuario

#### [MODIFY] auth.py

El endpoint `/auth/login` ya devuelve `permissions` junto con el token. Se incluirán los `group_ids` del usuario en la respuesta para poder determinar si es administrador (grupo 1) en el frontend.

#### [NEW] Endpoint `GET /api/v1/security/me/permissions`

Nuevo endpoint que devuelve los permisos consolidados del usuario autenticado, combinando todos sus grupos. Útil para refrescar permisos sin re-login.

#### [MODIFY] security.py

- Agregar validación en `add_user_to_group` y `remove_user_from_group` para que Admin-Seguridad no pueda modificar miembros del grupo Administrador.
- Agregar endpoint `GET /api/v1/security/me/permissions` para obtener permisos consolidados.

#### [MODIFY] deps.py

- Mejorar `require_permission` para también verificar si el usuario pertenece al grupo Administrador (group_id=1), no solo por `priv_admin`.

#### [MODIFY] main.py

- Proteger los endpoints de mantenimiento y usuarios con `require_permission` usando las apps granulares correspondientes.

---

### Componente 3: Backend — Protección de usuarios (Admin-Seguridad)

#### [MODIFY] main.py

En los endpoints CRUD de usuarios, agregar validación: si el usuario actual pertenece al grupo Admin-Seguridad (y no al grupo Administrador), no puede crear/editar/borrar usuarios que pertenezcan al grupo Administrador.

---

### Componente 4: Frontend — Store de permisos (Pinia)

#### [NEW] `frontend/src/stores/permissions.ts`

Store que:
- Almacena los permisos recibidos del login (`permissions` + `group_ids`).
- Expone helpers: `hasAccess(appName)`, `canCreate(appName)`, `canEdit(appName)`, `canDelete(appName)`, `canExport(appName)`, `canPrint(appName)`.
- Expone `isAdmin` (computed basado en si pertenece al grupo 1 o `priv_admin === 'Y'`).
- Persiste en `localStorage` para sobrevivir refresh.

#### [MODIFY] `frontend/src/stores/auth.ts`

- Al hacer login, guardar `permissions` y `group_ids` en el store de permisos.
- Al hacer logout, limpiar el store de permisos.

---

### Componente 5: Frontend — Filtrado de menús en sidebar

#### [MODIFY] `frontend/src/views/LayoutView.vue`

- Importar el store de permisos.
- Cada ítem de `navItems` tendrá un `appName` asociado (ej: `dashboard`, `checkin`, `active_visits`, etc.).
- Cada ítem de `maintenanceItems` tendrá su `appName` (ej: `maint_provinces`, etc.).
- Cada ítem de `securityItems` tendrá su `appName` (ej: `sec_users`, `sec_groups`, etc.).
- Usar `v-if="permissionsStore.hasAccess(item.appName)"` para mostrar/ocultar ítems.
- Las secciones "Mantenimiento" y "Seguridad" completas se ocultan si no tienen ningún ítem visible.
- Agregar nueva entrada de menú para "Miembros por Grupo" en seguridad.
- Agregar nueva entrada de menú para "Permisos por Grupo" en seguridad.

---

### Componente 6: Frontend — Guard de rutas

#### [MODIFY] `frontend/src/router/index.ts`

- Cada ruta tendrá un campo `meta.appName` que mapea a la app de permisos.
- En el `beforeEach`, verificar que el usuario tenga `hasAccess` para el `appName` de la ruta destino.
- Si no tiene acceso, redirigir a `/` (dashboard) o mostrar una página de acceso denegado.
- Agregar ruta para "Miembros por Grupo" (`/security/members`).
- Agregar ruta para "Permisos por Grupo" (`/security/permissions`).

---

### Componente 7: Frontend — Página de Miembros por Grupo (solo visualización)

#### [NEW] `frontend/src/views/security/GroupMembersView.vue`

Página que:
- Muestra un `vue-multiselect` de selección única para elegir un grupo.
- Al seleccionar un grupo, muestra la lista de usuarios miembros.
- Solo es de visualización (la gestión de membresía se hace en el formulario de usuario).
- Solo visible para miembros de los grupos Administrador y Admin-Seguridad.

---

### Componente 8: Frontend — Mejora de la vista de permisos

#### [MODIFY] `frontend/src/views/security/GroupPermissionsView.vue`

- Actualizar para usar las nuevas apps granulares.
- Mejorar el `loadGroups` para que use `description` como label del multiselect (actualmente usa `name` que no existe en el modelo — el campo es `description`).
- El multiselect de grupo funciona correctamente con `label="description"` y `track-by="group_id"`.
- Mejorar la tabla para agrupar apps por tipo (`page`, `crud`, `module`).

---

### Componente 9: Frontend — Protección de acciones en CRUDs

En los componentes que usan el CRUD genérico y las vistas individuales:
- El botón "Nuevo" se muestra solo si `canCreate(appName)`.
- El botón "Editar" se muestra solo si `canEdit(appName)`.
- El botón "Eliminar" se muestra solo si `canDelete(appName)`.
- El botón "Exportar" se muestra solo si `canExport(appName)`.
- El botón "Imprimir" se muestra solo si `canPrint(appName)`.

#### [MODIFY] `frontend/src/components/CrudTable.vue`

- Agregar prop `appName` para recibir el nombre de la app.
- Usar el store de permisos para mostrar/ocultar botones de acción.

#### Modificar todas las vistas de mantenimiento para pasar `appName` al CrudTable.

---

## Resumen de archivos

### Backend
| Acción | Archivo |
|--------|---------|
| NEW | Migración Alembic (seed apps + permisos) |
| MODIFY | `backend/app/api/v1/auth.py` — agregar `group_ids` a respuesta |
| MODIFY | `backend/app/api/v1/security.py` — endpoint `/me/permissions`, validación Admin-Seguridad |
| MODIFY | `backend/app/api/deps.py` — mejorar `require_permission` |
| MODIFY | `backend/app/main.py` — proteger endpoints con `require_permission` |

### Frontend
| Acción | Archivo |
|--------|---------|
| NEW | `frontend/src/stores/permissions.ts` |
| NEW | `frontend/src/views/security/GroupMembersView.vue` |
| MODIFY | `frontend/src/stores/auth.ts` — integrar permisos |
| MODIFY | `frontend/src/views/LayoutView.vue` — filtrar menús |
| MODIFY | `frontend/src/router/index.ts` — guards + nuevas rutas |
| MODIFY | `frontend/src/views/security/GroupPermissionsView.vue` — apps granulares |
| MODIFY | `frontend/src/components/CrudTable.vue` — permisos en acciones |
| MODIFY | Vistas de mantenimiento (pasar `appName`) |

---

## Verification Plan

### Automated Tests
1. **Backend**: Ejecutar el servidor y probar endpoints con diferentes usuarios:
   - `sysadmin` (grupo Administrador): debe tener acceso total.
   - `usuariodemo` (grupos Usuarios + Seguridad): debe ver dashboard, visitantes, checkin, checkout, visitas activas, historial.
   - `admindemo` (grupos Usuarios + Seguridad + Admin-Seguridad): como Seguridad + CRUD usuarios (excepto admins).

2. **Frontend**: Verificar en el navegador:
   - Login como `sysadmin` → todos los menús visibles.
   - Login como `usuariodemo` → solo menús permitidos.
   - Login como `admindemo` → menús de seguridad visibles, pero no puede editar/borrar usuarios administradores.
   - Intentar acceder a ruta prohibida → redirige al dashboard.

### Manual Verification
- Verificar la página "Miembros por Grupo" con diferentes usuarios.
- Verificar la matriz de permisos con las nuevas apps.
- Verificar que los botones de acción se ocultan según permisos.
