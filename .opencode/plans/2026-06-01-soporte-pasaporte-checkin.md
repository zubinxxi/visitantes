# Plan de Implementación: Soporte de Pasaporte en Check-In

Basado en spec aprobado: `docs/superpowers/specs/2026-06-01-soporte-pasaporte-checkin.md`

## Tareas

### 1. Backend — Modificar `_parse_qr_data` en `checkin.py`

**Archivo:** `backend/app/api/v1/checkin.py`

**Edición:** Insertar bloque de pasaporte antes del `raise HTTPException(400)`.

**Localización exacta:** Después de la línea 162 (`return {` para cédula manual), y antes de la línea 164 (`raise HTTPException(`).

**Código a insertar:**
```python
    if stripped:
        return {
            "id_card_number": stripped,
            "names": "",
            "surnames": "",
            "gender": "M",
            "province": "",
            "nationality": "",
            "id_num_control": "",
        }

```

**Verificación:** Ejecutar `python test_backend.py` o al menos arrancar el servidor y probar:

```bash
curl -X POST http://localhost:8000/api/v1/checkin/process-qr \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"raw_data": "PA123456"}'
```

Debe responder con `needs_registration: true` (si no existe) y `visitor_data.id_card_number = "PA123456"`.

### 2. Frontend — Actualizar textos en `CheckInView.vue`

**Archivo:** `frontend/src/views/CheckInView.vue`

**Ediciones:**
1. **Línea 517-518:** Cambiar texto informativo de:
   ```
   Escanee el código QR de la cédula o ingrese el número de cédula manualmente (ej: 8-7777-8888)
   ```
   a:
   ```
   Escanee el código QR de la cédula o ingrese el número de cédula o pasaporte manualmente
   ```

2. **Línea 526:** Cambiar placeholder de:
   ```
   Escanee o escriba el número de cédula...
   ```
   a:
   ```
   Escanee cédula o escriba cédula / pasaporte...
   ```

### 3. Verificación

1. Arrancar backend: `PYTHONPATH=. uvicorn app.main:app --reload`
2. Arrancar frontend: `npm run dev`
3. Probar flujo con pasaporte que NO existe (ej: `PA999999`):
   - Debe mostrar formulario de registro con número precargado
4. Probar flujo con pasaporte que SÍ existe:
   - Debe mostrar confirmación de check-in directa
5. Probar flujo con cédula (QR y manual):
   - Debe seguir funcionando exactamente como antes
6. Ejecutar linter y type-check:
   - `npm run type-check`
   - `npm run lint`

### 4. Comentarios finales

- No requiere migraciones de BD
- No requiere cambios en modelos/schemas
- No requiere nuevos endpoints
- El campo `id_card_number` ya es `unique=True` — pasaportes y cédulas conviven sin colisión
