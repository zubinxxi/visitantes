# Plan: Selector de Tipo de Procedimiento en Check-In

## Resumen

Reemplazar el campo de texto libre "Propósito de la visita" por un vue-multiselect (single-select) poblado desde la tabla `type_of_procedure`. La descripción seleccionada se guarda como `purpose` y el ID como `id_type_of_proce`.

## Archivos a modificar

1. `backend/app/api/v1/checkin.py` — schema + endpoint
2. `frontend/src/views/CheckInView.vue` — refs, carga, template, confirm, reset

---

## 1. Backend

### 1a. Schema `ConfirmCheckInRequest` (checkin.py ~línea 39)

Añadir campo opcional:

```python
class ConfirmCheckInRequest(BaseModel):
    visit_id: Optional[int] = None
    visitor_id: Optional[int] = None
    uadm_ids: List[int] = []
    building_ids: List[int] = []
    company_represents: str = ""
    purpose: str = ""
    id_type_of_proce: Optional[int] = None  # NUEVO
```

### 1b. Endpoint `confirm_checkin()` (checkin.py ~línea 347)

Antes del bloque de auditoría (`ip_user = ...`), añadir:

```python
    if payload.id_type_of_proce is not None:
        visit.id_type_of_proce = payload.id_type_of_proce
```

---

## 2. Frontend

### 2a. Nuevos refs (junto a `confirmCompanyRepresents` / `confirmPurpose`, ~línea 65)

```typescript
const procedureOptions = ref<{ id: number; description: string }[]>([])
const selectedProcedure = ref<{ id: number; description: string } | null>(null)
```

### 2b. Cargar opciones en `loadOptions()` (~línea 117)

```typescript
async function loadOptions() {
    const [uadmRes, buildingRes, procRes] = await Promise.all([
        api.get('/maintenance/uadms/', { params: { limit: 100 } }),
        api.get('/maintenance/buildings/', { params: { limit: 100 } }),
        api.get('/maintenance/procedures/', { params: { limit: 100 } }),
    ])
    uadmOptions.value = uadmRes.data.items || uadmRes.data
    buildingOptions.value = buildingRes.data.items || buildingRes.data
    procedureOptions.value = procRes.data.items || procRes.data
}
```

### 2c. Reemplazar input de propósito por Multiselect (~línea 765-775)

```html
<div>
    <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
        Propósito de la visita <span class="text-error-500">*</span>
    </label>
    <Multiselect
        v-model="selectedProcedure"
        :options="procedureOptions"
        :searchable="true"
        :close-on-select="true"
        :multiple="false"
        placeholder="Seleccione el propósito..."
        label="description"
        track-by="id"
        class="multiselect-dark"
    />
</div>
```

### 2d. Actualizar `confirmCheckIn()` (~línea 346)

En el payload, reemplazar `purpose: confirmPurpose.value` por:

```typescript
purpose: selectedProcedure.value?.description || '',
// Añadir al payload
id_type_of_proce: selectedProcedure.value?.id || 6,
```

Y eliminar `confirmPurpose` de los refs, loadOptions y resetForm.

### 2e. Actualizar `resetForm()` (~línea 477)

Añadir:
```typescript
selectedProcedure.value = null
```

### 2f. Limpiar ref innecesario

Eliminar `const confirmPurpose = ref('')` (~línea 66).

---

## 3. Verificación

```bash
# Backend: arrancar servidor
cd backend && source .venv/bin/activate && PYTHONPATH=. uvicorn app.main:app --reload

# Frontend: type-check y lint
cd frontend && npm run type-check && npm run lint
```

Probar flujo completo en el navegador:
1. Escanear cédula / ingresar pasaporte
2. En la pantalla de confirmación, verificar que aparezca el Multiselect con opciones de `type_of_procedure`
3. Seleccionar un propósito y confirmar check-in
4. Verificar en BD que `visits.purpose` = descripción y `visits.id_type_of_proce` = ID seleccionado
