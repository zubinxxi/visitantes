# Visitantes AMP Frontend

Aplicación web de gestión de visitantes para la Autoridad de los Asuntos de Indígenas (AAPI). Desarrollada con **Vue 3**, **Vite**, **TypeScript**, **Pinia** y **Tailwind CSS v4**. Diseño basado en la plantilla **TailAdmin Vue**.

## Tecnologías

| Categoría | Paquete | Versión |
| :--- | :--- | :--- |
| Framework | Vue 3 (Composition API + `<script setup>`) | ^3.5.x |
| Build Tool | Vite | ^8.x |
| Lenguaje | TypeScript | ~6.0.0 |
| Estado | Pinia | ^3.x |
| Enrutador | Vue Router | ^5.x |
| HTTP | Axios | ^1.x |
| UI | Tailwind CSS 4 + daisyui | ^4.x |
| QR Scanner | html5-qrcode | ^2.x |
| QR Generator | qrcode | ^1.x |
| Selectores | vue-multiselect | ^3.x |
| Exportación | xlsx | ^0.18.x |
| Fuente | Outfit (Google Fonts) | — |
| Linting | oxlint + ESLint | — |
| Testing | Vitest + jsdom | — |

## Estilo visual

El frontend utiliza el sistema de diseño de **TailAdmin Vue**:

- **Color primario**: `brand-500` (#465fff)
- **Escala de grises**: gray-25 → gray-950
- **Tipografía**: Outfit (Google Fonts)
- **Sidebar**: blanco con borde derecho, colapsable (90px / 290px), hover expand
- **Header**: blanco sticky con breadcrumbs
- **Tarjetas**: fondo blanco, borde gray-200, sombra sutil
- **Tablas**: header con fondo gray-50, texto uppercase gray-400
- **Formularios**: inputs h-11, bordes gray-300, focus ring brand-500
- **Botones**: brand-500 con sombra, bordes redondeados lg
- **Modo oscuro**: soporte completo vía store `theme.ts`

## Requisitos

- Node.js `^20.19.0` o `>=22.12.0`
- Backend corriendo en `http://localhost:8000`

## Instalación

```sh
npm install
```

## Desarrollo

```sh
npm run dev
```

Servidor en `http://localhost:5173` con proxy de `/api` y `/photos` al backend.

## Producción

```sh
npm run build
```

Los archivos compilados se generan en `dist/`.

## Scripts

| Comando | Descripción |
| :--- | :--- |
| `npm run dev` | Servidor de desarrollo con hot-reload |
| `npm run build` | Type-check + compilación para producción |
| `npm run preview` | Vista previa del build |
| `npm run type-check` | Type-check con vue-tsc |
| `npm run test:unit` | Pruebas unitarias con Vitest |
| `npm run lint` | Linting: oxlint + ESLint |

## Vistas

### Públicas (sin autenticación)

| Ruta | Vista | Descripción |
| :--- | :--- | :--- |
| `/login` | `LoginView.vue` | Inicio de sesión (split layout) |
| `/forgot-password` | `ForgotPasswordView.vue` | Solicitud de restablecimiento de contraseña |
| `/reset-password` | `ResetPasswordView.vue` | Restablecimiento con token |

### Dashboard (layout con sidebar)

| Ruta | Vista | `appName` | Descripción |
| :--- | :--- | :--- | :--- |
| `/` | `DashboardView.vue` | `dashboard` | Estadísticas, visitas recientes, accesos rápidos |
| `/checkin` | `CheckInView.vue` | `checkin` | QR scanner + formulario de registro dual |
| `/checkout` | `CheckoutView.vue` | `checkout` | Checkout rápido por entrada manual o QR |
| `/active` | `ActiveVisitsView.vue` | `active_visits` | Visitas activas con checkout, edición e impresión |
| `/history` | `VisitHistoryView.vue` | `visit_history` | Historial con filtros, paginación y exportación |
| `/visitors` | `VisitorsView.vue` | `visitors` | Búsqueda, listado, creación y detalles |
| `/config` | `ConfigView.vue` | `config` | Configuraciones del sistema (clave-valor) |

### Mantenimiento

| Ruta | Vista | `appName` |
| :--- | :--- | :--- |
| `/maintenance/provinces` | `ProvincesMaintenance.vue` | `maint_provinces` |
| `/maintenance/institutions` | `InstitutionsMaintenance.vue` | `maint_institutions` |
| `/maintenance/type-uadm` | `TypeUadmMaintenance.vue` | `maint_type_uadm` |
| `/maintenance/buildings` | `BuildingMaintenance.vue` | `maint_buildings` |
| `/maintenance/procedures` | `TypeOfProcedureMaintenance.vue` | `maint_procedures` |
| `/maintenance/uadms` | `UadmMaintenance.vue` | `maint_uadms` |

### Seguridad

| Ruta | Vista | `appName` |
| :--- | :--- | :--- |
| `/security/users` | `UsersMaintenance.vue` | `sec_users` |
| `/security/groups` | `GroupsMaintenance.vue` | `sec_groups` |
| `/security/apps` | `AppsMaintenance.vue` | `sec_apps` |
| `/security/permissions` | `GroupPermissionsView.vue` | `sec_permissions` |
| `/security/members` | `GroupMembersView.vue` | `sec_members` |

## Stores (Pinia)

| Store | Archivo | Descripción |
| :--- | :--- | :--- |
| `useAuthStore` | `stores/auth.ts` | Autenticación: login, logout, cambio/recuperación de contraseña. Persiste token en localStorage |
| `usePermissionsStore` | `stores/permissions.ts` | Permisos por aplicación con 6 privilegios más `isAdmin`. Persiste en localStorage con versionado |
| `useThemeStore` | `stores/theme.ts` | Tema oscuro/claro. Persiste en localStorage, controla clase `dark` en `<html>` |

## Componentes

| Componente | Archivo | Descripción |
| :--- | :--- | :--- |
| `CrudTable` | `components/CrudTable.vue` | Tabla CRUD genérica con columnas configurables, búsqueda, paginación, modal de formulario, confirmación de eliminación, exportación e impresión. Integra permisos granulares. Usa vue-multiselect |
| `Modal` | `components/Modal.vue` | Modal genérico con slots header/footer, tamaños sm/md/lg/xl, teleport al body |
| `ToastContainer` | `components/ToastContainer.vue` | Notificaciones toast (success/error/warning/info) con auto-destrucción |
| `VisitorBadge` | `components/VisitorBadge.vue` | Gafete de visitante para impresión térmica. 4 plantillas: 4x3, 3x4, 2x4, 4x2 pulgadas. Genera QR internamente |
| `BadgePrintPreview` | `components/BadgePrintPreview.vue` | Modal de previsualización de gafetes con selección de tamaño de etiqueta |

## Composables

| Composable | Archivo | Descripción |
| :--- | :--- | :--- |
| `useCrud` | `composables/useCrud.ts` | Lógica CRUD genérica: lista paginada, formulario crear/editar, eliminación, exportación Excel, impresión |
| `useToast` | `composables/useToast.ts` | Sistema de notificaciones toast (estado global singleton) |
| `useSidebar` | `composables/useSidebar.ts` | Estado del sidebar colapsable: collapsed, mobile, hover |
| `useBadgePrinter` | `composables/useBadgePrinter.ts` | Selección de visitas para impresión de gafetes, generación de QR |

## Permisos

Cada ruta protegida tiene un `appName` en `meta`. El guard de navegación (`beforeEach`) verifica:
- Si hay token JWT en localStorage
- Si el usuario tiene `priv_access` para el `appName` mediante `usePermissionsStore.hasAccess()`
- Si `isAdmin` (`priv_admin === 'Y'` o grupo ID 1), otorga acceso total

Los 6 privilegios por aplicación se chequean desde las vistas:

| Método | Privilegio |
| :--- | :--- |
| `canCreate(appName)` | `priv_insert` |
| `canEdit(appName)` | `priv_update` |
| `canDelete(appName)` | `priv_delete` |
| `canExport(appName)` | `priv_export` |
| `canPrint(appName)` | `priv_print` |

## Estructura del proyecto

```
src/
├── assets/
│   ├── base.css           # Resets y variables base
│   └── main.css           # Tailwind + tema TailAdmin
├── components/
│   ├── BadgePrintPreview.vue
│   ├── CrudTable.vue
│   ├── Modal.vue
│   ├── ToastContainer.vue
│   └── VisitorBadge.vue
├── composables/
│   ├── useBadgePrinter.ts
│   ├── useCrud.ts
│   ├── useSidebar.ts
│   └── useToast.ts
├── lib/
│   └── api.ts             # Axios con interceptors (auth, 401 redirect)
├── router/
│   └── index.ts           # Rutas + guards de autenticación y permisos
├── stores/
│   ├── auth.ts            # Login/logout, sesión JWT persistente
│   ├── permissions.ts     # Permisos granulares con 6 privilegios
│   └── theme.ts           # Modo oscuro/claro
├── types/
│   ├── labelSize.ts       # Tamaños de etiqueta para impresión
│   └── visit.ts           # Interfaces: Visit, Visitor, VisitStats
├── views/
│   ├── ActiveVisitsView.vue
│   ├── CheckInView.vue
│   ├── CheckoutView.vue
│   ├── ConfigView.vue
│   ├── DashboardView.vue
│   ├── ForgotPasswordView.vue
│   ├── LayoutView.vue
│   ├── LoginView.vue
│   ├── ResetPasswordView.vue
│   ├── VisitHistoryView.vue
│   ├── VisitorsView.vue
│   ├── maintenance/
│   │   ├── AppsMaintenance.vue
│   │   ├── BuildingMaintenance.vue
│   │   ├── GroupsMaintenance.vue
│   │   ├── InstitutionsMaintenance.vue
│   │   ├── ProvincesMaintenance.vue
│   │   ├── TypeOfProcedureMaintenance.vue
│   │   ├── TypeUadmMaintenance.vue
│   │   ├── UadmMaintenance.vue
│   │   └── UsersMaintenance.vue
│   └── security/
│       ├── GroupMembersView.vue
│       └── GroupPermissionsView.vue
├── App.vue
└── main.ts
```

## Credenciales de prueba

| Usuario | Contraseña |
| :--- | :--- |
| sysadmin | 123456 |
| admindemo | 123456 |
| usuariodemo | 123456 |

## IDE recomendado

[Visual Studio Code](https://code.visualstudio.com/) + extensión [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (deshabilitar Vetur).
