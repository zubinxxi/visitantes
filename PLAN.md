# Sistema de Gestión de Visitantes - `visitorsdb`

## Información del Proyecto

- **Backend:** FastAPI + SQLModel (Async)
- **Frontend:** Vue.js 3 + Pinia + Tailwind CSS (estilo TailAdmin)
- **BD:** MariaDB (localhost, DB: `visitorsdb`)
- **Password hash:** bcrypt (rounds=12)
- **Permisos:** `sec_groups_apps` (grupo ↔ app)

---

## Plan de Fases

### ✅ Fase 1 — Backend Base (COMPLETADA)
- [x] FastAPI + SQLModel + asyncmy
- [x] Config con `python-dotenv` (credenciales en `.env`)
- [x] Modelos SQLModel para todas las tablas
- [x] Schemas Pydantic (Create/Read/Update)
- [x] Patrón `SessionDep` con `Annotated`
- [x] `lifespan` para eventos de startup/shutdown
- [x] Migración passwords → bcrypt
- [x] Alembic (visits_buildings + sec_apps)
- [x] CRUD mantenimiento (9 recursos)
- [x] Auth login (JWT + permisos `sec_groups_apps`)
- [x] `.gitignore` + `.env.example`

### ✅ Fase 2 — Lógica de Negocio (COMPLETADA)
- [x] Endpoint QR parseo cédula
- [x] Endpoint upload foto webcam
- [x] Check-in/Check-out completo
- [x] Deduplicación por cédula
- [x] Auditoría en tabla sc_log

### ✅ Fase 3 — Frontend (COMPLETADA)
- [x] Vue 3 + Vite + Pinia + Tailwind (`npm create vue@latest`)
- [x] Estilo TailAdmin Vue (colores brand, sidebar blanco, tarjetas, tablas)
- [x] Login split-layout con panel brand-950
- [x] Sidebar colapsable (90px / 290px) con iconos SVG
- [x] Header sticky con breadcrumbs y notificaciones
- [x] Dashboard con 4 tarjetas estadísticas + tabla + acciones rápidas
- [x] CheckIn con QR Scanner (html5-qrcode + WebRTC) + formulario
- [x] Visitas Activas (tabla con avatar, tiempo transcurrido, checkout)
- [x] Visitantes (búsqueda por cédula, listado, modal detalles)
- [x] ESLint + oxlint + TypeScript estricto
- [x] Fuente Outfit (Google Fonts)
- [x] Tema Tailwind personalizado (colores brand, gray, success, error, warning)

### 🖨️ Fase 4 — Impresión (PENDIENTE)
- [ ] VisitorBadge.vue (etiqueta térmica)
- [ ] CSS `@media print`
- [ ] Integración `print-js`

---

## Endpoints

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Login → JWT + permisos `sec_groups_apps` |

### 👥 Visitantes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visitors/` | Listar todos |
| `GET` | `/api/v1/visitors/{visitor_id}` | Por ID |
| `GET` | `/api/v1/visitors/cedula/{cedula}` | Por cédula |
| `POST` | `/api/v1/visitors/` | Crear (requiere auth) |
| `PUT` | `/api/v1/visitors/{visitor_id}` | Actualizar |
| `DELETE` | `/api/v1/visitors/{visitor_id}` | Eliminar |

### 📋 Visitas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visits/` | Listar todas |
| `GET` | `/api/v1/visits/active` | Activas (sin checkout) |
| `GET` | `/api/v1/visits/today` | Visitas del día |
| `GET` | `/api/v1/visits/stats/summary` | Estadísticas |
| `POST` | `/api/v1/visits/checkin` | Check-in completo |
| `POST` | `/api/v1/visits/{visit_id}/checkout` | Check-out |

### 📱 QR

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/qr/parse` | Parsear QR cédula panameña |

---

## Usuarios de prueba

Todos con password `123456`:

| login | name | groups |
|-------|------|--------|
| sysadmin | Administrador | 1 |
| admindemo | Administrador Demo | 2, 3, 4 |
| usuariodemo | Usuario Demo | 2, 3 |
