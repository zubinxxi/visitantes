# Plan de Mejoras y Correcciones - Visitantes AMP

## 1. Correcciones Críticas (correciones_y_reglas.txt)

### 1.1 Check-In: Mover campos company_represents y purpose
**Archivo:** `frontend/src/views/CheckInView.vue`
**Problema:** Los campos están en el formulario de "Registrar Nuevo Visitante" (líneas 111-112) y también en "Confirmar Check-In".
**Corrección:** Remover `company_represents` y `purpose` del `registerForm` (líneas 111-112, 296-298). Mantenerlos solo en la sección de confirmación (líneas 686-710).

### 1.2 Corregir vue-multiselect (mostrar label, no value)
**Verificar en:**
- `frontend/src/views/VisitorsView.vue` - Revisar `SearchableSelectSingle` para género y provincia
- `frontend/src/views/maintenance/UsersMaintenance.vue` - Campos con valores Y/N deben mostrar Sí/No
- `frontend/src/components/SearchableSelectSingle.vue` - Verificar implementación

**Corrección:** Asegurar que los componentes usen `label` para display y `value` para el modelo.

### 1.3 Impresión de etiquetas (tamaño correcto)
**Archivos:** `frontend/src/views/CheckInView.vue`, `frontend/src/components/VisitorBadge.vue`
**Problema:** Se imprime en tamaño A4 en lugar del tamaño de etiqueta.
**Corrección:**
- En `printBadge()` (línea 367-416): Usar CSS `@page { size: ... }` ya está presente, pero verificar que se aplique correctamente
- Simplificar: Imprimir directamente el componente `VisitorBadge` usando `window.print()` con media queries adecuadas
- El archivo `VisitorBadge.vue` ya tiene estilos `@media print` (línea 151), pero el `printBadge()` usa `window.open` que puede ignorar estos estilos

### 1.4 Dashboard: Enlace rápido a Checkout
**Archivo:** `frontend/src/views/DashboardView.vue`
**Corrección:** Agregar tarjeta de "Checkout Rápido" en Acciones Rápidas (línea 169-208) con input para escanear QR y procesar salida, mostrando notificación y regresando al dashboard.

### 1.5 Dashboard: Actualizar datos reales
**Estado:** ✅ Implementado correctamente (líneas 22-25 usan API)

### 1.6 Historial de Visitas: Filtros y distribución
**Archivo:** `frontend/src/views/VisitHistoryView.vue`
**Problemas:**
- El filtro de fecha (`filterDate`) no se envía en `loadVisits()` (línea 35-62)
- Los inputs no tienen el mismo ancho (línea 118-166)

**Corrección:**
```javascript
// En loadVisits(), agregar:
if (filterDate.value) {
  params.date = filterDate.value
}
```
- Ajustar clases Tailwind para que todos los inputs tengan `flex-1` excepto el botón
- Agregar soporte de filtrado por fecha en backend (`backend/app/api/v1/visits.py`)

### 1.7 Usuarios: vue-multiselect para permisos y grupos
**Archivo:** `frontend/src/views/maintenance/UsersMaintenance.vue`
**Problema:** No tiene selección de grupos ni campos Y/N muestran value.
**Corrección:**
- Modificar para usar `CrudTable` con columnas personalizadas o crear formulario personalizado
- Agregar campo `groups` (selección múltiple) que cargue de `/maintenance/groups`
- Campos `active` y `priv_admin` deben usar vue-multiselect con labels "Sí"/"No"

### 1.8 Visitantes: vue-multiselect para género y provincia
**Archivo:** `frontend/src/views/VisitorsView.vue`
**Corrección:**
- Género (línea 765): Cambiar `SearchableSelectSingle` por `vue-multiselect` con `:multiple="false"`
- Provincia (línea 778): Cambiar por `vue-multiselect` con carga desde API

### 1.9 Unidades Administrativas: vue-multiselect para catálogos
**Archivo:** `frontend/src/views/maintenance/UadmMaintenance.vue`
**Problema:** Usa `useCrud` genérico que no soporta selects personalizados para llaves foráneas.
**Corrección:** Crear formulario personalizado en lugar de `CrudTable` genérico, usando vue-multiselect para:
- `id_institution` ← `/maintenance/institutions`
- `id_province` ← `/maintenance/provinces`
- `id_district`, `id_district_subdivision` ← nuevos catálogos o agregar
- `id_type_uadm` ← `/maintenance/type-uadm`
- `id_uadm_origin` ← `/maintenance/uadms` (autorreferencia)

### 1.10 Cambiar "Tipos de Procedimientos" por "Tipo de Trámite"
**Buscar en:** `frontend/src/views/maintenance/TypeOfProcedureMaintenance.vue`
**Corrección:** Cambiar título y etiquetas.

### 1.11 Módulo de Seguridad (Permisos por Grupos)
**Nuevo archivo:** `frontend/src/views/security/GroupPermissionsView.vue`
**Backend necesita:**
- Endpoint para listar usuarios por grupo: `GET /api/v1/security/groups/{group_id}/users`
- Endpoint para asignar/remover usuarios a grupos: `POST /api/v1/security/groups/{group_id}/users`
- Endpoint para CRUD de permisos `sec_groups_apps` ya existe en `/api/v1/maintenance/group_apps`

**Frontend:**
- Página con vue-multiselect para seleccionar grupo (única selección)
- Mostrar usuarios miembros del grupo seleccionado
- Matriz de permisos: checkbox para cada app y privilegio (access, insert, update, delete, export, print)
- Lógica de permisos:
  - Admin: todos los permisos
  - Usuario: dashboard, editar perfil
  - Seguridad: dashboard, ver/agregar/editar/borrar visitantes, visitas activas, historial
  - Admin-Seguridad: igual que Seguridad + CRUD usuarios (excepto admin)

### 1.12 Sidebar: Mostrar correo del usuario
**Archivo:** `frontend/src/views/LayoutView.vue`
**Corrección:** Línea 189, cambiar `auth.user?.role || 'Usuario'` por `auth.user?.email || auth.user?.login`

### 1.13 Diseño TailAdmin y Responsivo
**Verificar:** Las vistas principales ya usan clases Tailwind con breakpoints (`sm:`, `md:`, `lg:`).
**Corrección:** Revisar que todas las tablas usen `overflow-x-auto` y sean responsivas.

### 1.14 Tabla "config" y página de configuración
**Backend nuevo:**
- Modelo: `backend/app/models/config.py` (tabla `config`)
- Esquemas: `backend/app/schemas/config.py`
- Endpoints: `backend/app/api/v1/config.py` con CRUD
- Migración Alembic para crear tabla

**Frontend nuevo:**
- `frontend/src/views/ConfigView.vue`
- Agregar enlace en el dropdown de usuario en `LayoutView.vue` (línea 280-304)
- Solo accesible para miembros del grupo administrador

### 1.15 Quitar icono de notificaciones
**Archivo:** `frontend/src/views/LayoutView.vue`
**Corrección:** Remover líneas 246-252 (botón de campana).

---

## 2. Mejoras de Backend (Buenas Prácticas)

### 2.1 Corregir SessionDep en main.py
**Archivo:** `backend/app/main.py`
**Problema:** Línea 34 redefine `SessionDep = AsyncSession` incorrectamente.
**Corrección:**
```python
# Remover línea 34
# Agregar import correcto:
from app.api.deps import SessionDep
```

### 2.2 Limpiar logs de depuración
**Archivo:** `backend/app/api/deps.py`
**Corrección:** Remover `logger.warning(f"DEBUG: ...")` de las líneas 47, 50, 61.

### 2.3 Proteger endpoints con permisos sec_groups_apps
**Archivo:** `backend/app/api/deps.py`
**Nueva dependencia:**
```python
def require_permission(app_name: str, privilege: str = "priv_access"):
    # Verificar que user tiene el privilegio en sec_groups_apps para la app
```

### 2.4 Endpoint para sec_users_groups
**Archivo nuevo:** `backend/app/api/v1/security.py`
**Endpoints:**
- `GET /api/v1/security/groups/{group_id}/users`
- `POST /api/v1/security/groups/{group_id}/users/{user_login}`
- `DELETE /api/v1/security/groups/{group_id}/users/{user_login}`

### 2.5 Configurar Alembic correctamente
**Archivo:** `backend/alembic/env.py`
**Corrección:** Cambiar `target_metadata = None` por:
```python
from app.models import SQLModel
target_metadata = SQLModel.metadata
```

### 2.6 Migración inicial
Crear migración que incluya todas las tablas existentes:
```bash
source .venv/bin/activate
PYTHONPATH=. alembic -c alembic.ini revision -m "initial_migration" --autogenerate
```

---

## 3. Orden de Implementación Recomendado

1. **Backend:**
   - 2.1 Corregir SessionDep en main.py
   - 2.2 Limpiar logs de depuración
   - 2.5 Configurar Alembic
   - 2.6 Crear migración inicial
   - 1.14 Tabla config (modelo, esquema, endpoint)
   - 2.4 Endpoints sec_users_groups
   - 2.3 Proteger endpoints con permisos

2. **Frontend:**
   - 1.15 Quitar icono notificaciones
   - 1.12 Sidebar mostrar correo
   - 1.1 Check-In mover campos
   - 1.2 Corregir vue-multiselect
   - 1.7 Usuarios con grupos
   - 1.8 Visitantes con multiselect
   - 1.9 UADM con multiselect
   - 1.6 Historial filtros
   - 1.3 Impresión etiquetas
   - 1.4 Dashboard checkout rápido
   - 1.10 Cambiar etiqueta procedimientos
   - 1.11 Módulo seguridad
   - 1.14 Página configuración

---

## 4. Comandos para Verificación

### Backend
```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

### Lint y Type Check
```bash
cd frontend
npm run lint
npm run type-check
```

### Tests
```bash
cd frontend
npm run test:unit
```

---

## 5. Notas Adicionales

- **Idioma:** Todo el código, comentarios y respuestas en español (convención del proyecto)
- **Vue:** Composition API + `<script setup>` obligatorio
- **UI:** Mantener diseño TailAdmin Vue + Tailwind CSS + daisyui
- **FastAPI:** Pydantic v2, tipado estático, `SessionDep` con `Annotated`
- **Impresora:** Modelo 168BT/168, referencias en AGENTS.md
