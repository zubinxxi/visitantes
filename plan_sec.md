# 🔒 Plan de Auditoría de Seguridad — Visitantes AMP

> Documento generado tras el análisis exhaustivo del código fuente (backend + frontend).
> Fecha: 2026-05-18

---

## Resumen Ejecutivo

Se identificaron **23 vulnerabilidades** clasificadas en 3 niveles de severidad. El proyecto tiene una base de seguridad razonable (bcrypt, JWT, permisos granulares) pero presenta deficiencias importantes en: validación de entradas, protección contra fuerza bruta, headers HTTP de seguridad, y gestión de archivos subidos.

---

## Clasificación de Severidad

| Símbolo | Nivel | Descripción |
|---------|-------|-------------|
| 🔴 | **CRÍTICA** | Explotable directamente, riesgo de compromiso total |
| 🟠 | **ALTA** | Riesgo significativo, requiere atención inmediata |
| 🟡 | **MEDIA** | Debilidad que debe corregirse en el corto plazo |
| 🔵 | **BAJA** | Mejora recomendada, buenas prácticas |

---

## Fase 1 — Vulnerabilidades Críticas (🔴)

### 1.1 🔴 Compatibilidad con hashes MD5 en `verify_password()`
- **Archivo:** `backend/app/core/security.py:23`
- **Problema:** Si el hash almacenado no empieza con `$2b$`/`$2a$`, se compara con MD5 (`hashlib.md5`). MD5 es criptográficamente roto; un atacante con acceso a la BD puede revertir contraseñas MD5 en segundos.
- **Riesgo:** Si existen usuarios legacy con hash MD5, sus contraseñas son trivialmente vulnerables.
- **Corrección:** Migrar todos los hashes MD5 a bcrypt al primer login exitoso (re-hash automático). Eliminar la rama MD5 una vez completada la migración.

### 1.2 🔴 Endpoint `upload-photo-temp` sin autenticación
- **Archivo:** `backend/app/api/v1/visitors.py:161-201`
- **Problema:** El endpoint `POST /api/v1/visitors/upload-photo-temp` no tiene ninguna dependencia de autenticación (`CurrentUser`, `require_permission`). Cualquier actor anónimo puede subir archivos al servidor.
- **Riesgo:** Escritura no autorizada de archivos al disco. Vector potencial de DoS (llenado de disco) y posible ejecución remota si se sube contenido malicioso.
- **Corrección:** Agregar dependencia `CurrentUser` o `require_permission("visitors", "priv_insert")`.

### 1.3 🔴 Endpoint `delete_visit` sin autenticación ni permisos
- **Archivo:** `backend/app/api/v1/visits.py:486-506`
- **Problema:** `DELETE /api/v1/visits/{visit_id}` no tiene ninguna dependencia de autenticación. Cualquier usuario (autenticado o no) puede eliminar visitas.
- **Riesgo:** Eliminación masiva de datos por actores no autorizados.
- **Corrección:** Agregar `dependencies=[Depends(require_permission("visitors", "priv_delete"))]` y verificación de `CurrentUser`.

### 1.4 🔴 Endpoints `get_all_visitors`, `get_visitor`, `update_visitor`, `delete_visitor` sin permisos
- **Archivo:** `backend/app/api/v1/visitors.py:18,62,96,111`
- **Problema:** Los endpoints `GET /visitors/`, `GET /visitors/{id}`, `PUT /visitors/{id}`, `DELETE /visitors/{id}` no tienen protección de autenticación ni permisos. Solo `POST /` y `GET /cedula/{cedula}` están protegidos.
- **Riesgo:** Lectura, modificación y eliminación no autorizada de datos de visitantes (PII: cédulas, nombres, fotos).
- **Corrección:** Agregar `require_permission("visitors", ...)` con el privilegio correspondiente a cada endpoint.

### 1.5 🔴 Endpoint `checkout-by-qr` acepta `dict` sin validación
- **Archivo:** `backend/app/api/v1/visits.py:327-362`
- **Problema:** El endpoint `checkout-by-qr` recibe `request: dict` en lugar de un schema Pydantic. No hay validación de tipos ni de campos, lo que permite inyección de datos arbitrarios.
- **Riesgo:** Bypass de validación, posibles errores inesperados, ataque de campos desconocidos.
- **Corrección:** Crear un schema Pydantic `CheckoutByQrRequest` con `visit_id: int`.

### 1.6 🔴 Endpoint `create_checkin` acepta `dict` sin validación
- **Archivo:** `backend/app/api/v1/visits.py:545-647`
- **Problema:** `POST /api/v1/visits/checkin` recibe `request: dict` crudo. Campos como `user_created` pueden ser spoofados por el cliente: `user_created = request.get("user_created", current_user.login)`.
- **Riesgo:** Un usuario puede falsificar quién creó un registro de check-in, comprometiendo la trazabilidad de auditoría.
- **Corrección:** Crear schema Pydantic, eliminar `user_created` del input y usar siempre `current_user.login`.

---

## Fase 2 — Vulnerabilidades Altas (🟠)

### 2.1 🟠 Sin rate limiting en login y forgot-password
- **Archivos:** `backend/app/api/v1/auth.py:33,81`
- **Problema:** Los endpoints `/auth/login` y `/auth/forgot-password` no tienen limitación de intentos. No existe middleware de rate limiting en toda la aplicación.
- **Riesgo:** Ataques de fuerza bruta sobre credenciales. Abuso del endpoint forgot-password para spam de correos.
- **Corrección:** Implementar `slowapi` o middleware personalizado con rate limiting (ej: 5 intentos/minuto en login, 3/hora en forgot-password).

### 2.2 🟠 Sin headers de seguridad HTTP
- **Problema:** No se configuran headers de seguridad: `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy`, `X-XSS-Protection`, `Referrer-Policy`.
- **Riesgo:** Vulnerable a clickjacking, MIME sniffing, falta de HSTS permite downgrade a HTTP.
- **Corrección:** Agregar middleware de headers de seguridad en `main.py`.

### 2.3 🟠 CORS permisivo con `allow_methods=["*"]` y `allow_headers=["*"]`
- **Archivo:** `backend/app/main.py:56-66`
- **Problema:** Se permiten todos los métodos y headers HTTP en CORS. En producción esto es excesivamente abierto.
- **Riesgo:** Amplía la superficie de ataque a métodos HTTP no necesarios (OPTIONS abuse, etc.).
- **Corrección:** Restringir a métodos utilizados (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) y headers específicos (`Authorization`, `Content-Type`).

### 2.4 🟠 Token JWT almacenado en localStorage
- **Archivo:** `frontend/src/stores/auth.ts:61`
- **Problema:** El token JWT se guarda en `localStorage`, accesible vía JavaScript. Si existe un XSS, el token puede ser exfiltrado.
- **Riesgo:** Robo de sesión mediante XSS.
- **Corrección recomendada:** Migrar a cookies `httpOnly` + `Secure` + `SameSite=Strict`. Alternativamente, mitigar XSS con CSP estricta.

### 2.5 🟠 Sin validación del contenido MIME de archivos subidos
- **Archivos:** `backend/app/api/v1/visitors.py:122-158,161-201`
- **Problema:** Se valida solo la extensión del archivo (`.jpg`, `.png`, etc.) pero no se verifica el contenido real (magic bytes). Un archivo `.jpg` con contenido PHP/HTML/SVG pasaría la validación.
- **Riesgo:** Upload de archivos maliciosos camuflados.
- **Corrección:** Validar magic bytes del archivo (ej: con `python-magic` o verificación manual de cabeceras) y procesar la imagen con Pillow para sanitizarla.

### 2.6 🟠 Archivos de base de datos SQLite en el directorio del proyecto
- **Archivos:** `backend/visitantes.db`, `backend/visitors.db`
- **Problema:** Existen archivos `.db` SQLite en el directorio del backend (posiblemente legacy). Si se sirven estáticamente o están accesibles, exponen datos.
- **Riesgo:** Fuga de datos si se accede al directorio del proyecto.
- **Corrección:** Eliminar archivos `.db` innecesarios, agregar `*.db` al `.gitignore`.

### 2.7 🟠 Escalación de privilegios vía `priv_admin` en `SecUserUpdate`
- **Archivo:** `backend/app/schemas/security.py:91-98`
- **Problema:** El schema `SecUserUpdate` permite actualizar `priv_admin`. Un usuario con permiso `sec_users:priv_update` (Admin-Seguridad) puede asignarse `priv_admin=Y` a sí mismo o a otros, escalando privilegios.
- **Riesgo:** Un usuario Admin-Seguridad puede convertirse en superadmin.
- **Corrección:** Bloquear la modificación de `priv_admin` en `update_user()` para usuarios que no sean `priv_admin=Y`. Solo un superadmin debería poder asignar ese campo.

---

## Fase 3 — Vulnerabilidades Medias (🟡)

### 3.1 🟡 IP hardcodeada `127.0.0.1` en logs de auditoría
- **Archivos:** `backend/app/api/v1/visits.py:27`, `backend/app/api/v1/checkin.py:67`
- **Problema:** La IP del usuario se registra siempre como `127.0.0.1` en `ScLog`. Se pierde trazabilidad real del origen de las acciones.
- **Corrección:** Extraer `request.client.host` del objeto `Request` de FastAPI y pasarlo al log.

### 3.2 🟡 Sin validación de longitud/complejidad de contraseña
- **Archivos:** `backend/app/schemas/security.py:82,102-103,110-112`
- **Problema:** `SecUserCreate.pswd`, `ChangePasswordRequest.new_password` y `ResetPasswordRequest.new_password` no tienen validaciones de longitud mínima ni complejidad.
- **Riesgo:** Contraseñas triviales como `1`, `123456` son aceptadas.
- **Corrección:** Agregar `min_length=8` y validador de complejidad (al menos una mayúscula, minúscula y dígito).

### 3.3 🟡 Endpoint `get_visit_badge` sin autenticación
- **Archivo:** `backend/app/api/v1/checkin.py:327-365`
- **Problema:** `GET /checkin/visits/{visit_id}/badge` no requiere autenticación. Cualquier persona que conozca un `visit_id` puede obtener los datos del gafete (nombre, cédula, destino).
- **Riesgo:** Fuga de información personal (PII).
- **Corrección:** Agregar dependencia `CurrentUser`.

### 3.4 🟡 Endpoint `/qr/parse` sin autenticación
- **Archivo:** `backend/app/api/v1/qr.py:28-48`
- **Problema:** `POST /api/v1/qr/parse` no requiere autenticación. Permite consultar si un visitante existe por cédula y obtener sus datos completos.
- **Riesgo:** Enumeración de visitantes por actores no autorizados.
- **Corrección:** Agregar dependencia `CurrentUser`.

### 3.5 🟡 Permisos y token almacenados en localStorage sin cifrado
- **Archivo:** `frontend/src/stores/permissions.ts:74-77`
- **Problema:** Los permisos, group_ids y priv_admin se almacenan en `localStorage` en texto plano. Un script XSS puede leer estos datos y determinar los privilegios del usuario.
- **Riesgo:** Reconocimiento de privilegios para ataques dirigidos.
- **Corrección:** Los permisos se deben validar siempre en el backend (ya se hace), pero minimizar la exposición en localStorage. Considerar `sessionStorage` como alternativa más restrictiva.

### 3.6 🟡 Docs de Swagger/OpenAPI expuestas en producción
- **Archivo:** `backend/app/main.py:49-54`
- **Problema:** FastAPI expone `/docs` y `/redoc` automáticamente. En producción, esto revela toda la superficie de la API.
- **Corrección:** Condicionar con `if not settings.DEBUG: docs_url=None, redoc_url=None`.

### 3.7 🟡 `python-jose` está descontinuado
- **Archivo:** `backend/requirements.txt:7`
- **Problema:** `python-jose` no ha recibido actualizaciones de seguridad significativas. La recomendación actual es migrar a `PyJWT` o `joserfc`.
- **Corrección:** Reemplazar `python-jose` por `PyJWT>=2.8.0`.

### 3.8 🟡 Sin validación de `active_filter` en visits
- **Archivo:** `backend/app/api/v1/visits.py:116,219`
- **Problema:** `active_filter` acepta cualquier string. No se valida contra valores permitidos (`"true"`, `"false"`, `""`).
- **Corrección:** Usar `Literal["true", "false", ""]` o un `Enum` para el query param.

---

## Fase 4 — Mejoras y Buenas Prácticas (🔵)

### 4.1 🔵 Agregar `*.db` al `.gitignore` del backend
### 4.2 🔵 Agregar `lang="es"` al `<html>` en `index.html` (actualmente `lang=""`)
### 4.3 🔵 Agregar `meta description` al `index.html` del frontend
### 4.4 🔵 Registrar IP real del cliente en la tabla `sc_log`
### 4.5 🔵 Agregar expiración de sesión por inactividad en el frontend (idle timeout)
### 4.6 🔵 Implementar token refresh (actualmente el token dura 480 minutos sin renovación)
### 4.7 🔵 Agregar logs estructurados con nivel `WARNING` para intentos de login fallidos

---

## Plan de Ejecución Propuesto

### Etapa 1 — Correcciones Críticas (1-2 días)
| # | Tarea | Archivo Principal |
|---|-------|-------------------|
| 1 | Eliminar verificación MD5 o migrar hashes | `core/security.py` |
| 2 | Agregar autenticación a `upload-photo-temp` | `api/v1/visitors.py` |
| 3 | Proteger `delete_visit` con permisos | `api/v1/visits.py` |
| 4 | Proteger endpoints de visitors sin auth | `api/v1/visitors.py` |
| 5 | Reemplazar `dict` con schemas Pydantic | `api/v1/visits.py` |
| 6 | Eliminar `user_created` del input del cliente | `api/v1/visits.py` |

### Etapa 2 — Correcciones Altas (2-3 días)
| # | Tarea | Archivo Principal |
|---|-------|-------------------|
| 7 | Implementar rate limiting con `slowapi` | `main.py` + nuevo middleware |
| 8 | Agregar headers de seguridad HTTP | `main.py` |
| 9 | Restringir CORS a métodos/headers específicos | `main.py` |
| 10 | Validar MIME type real de archivos subidos | `api/v1/visitors.py` |
| 11 | Eliminar archivos `.db` del proyecto | directorio `backend/` |
| 12 | Bloquear escalación de `priv_admin` | `api/v1/main.py` (update_user) |

### Etapa 3 — Correcciones Medias (1-2 días)
| # | Tarea | Archivo Principal |
|---|-------|-------------------|
| 13 | Registrar IP real del cliente en auditoría | `api/v1/visits.py`, `checkin.py` |
| 14 | Validar complejidad de contraseñas | `schemas/security.py` |
| 15 | Proteger `get_visit_badge` y `/qr/parse` | `api/v1/checkin.py`, `qr.py` |
| 16 | Ocultar Swagger/OpenAPI en producción | `main.py` |
| 17 | Migrar de `python-jose` a `PyJWT` | `core/security.py`, `requirements.txt` |
| 18 | Validar `active_filter` con Literal/Enum | `api/v1/visits.py` |

### Etapa 4 — Mejoras (opcional, 1 día)
| # | Tarea |
|---|-------|
| 19-25 | Items 4.1 a 4.7 listados arriba |

---

## Verificación Post-Correcciones

1. **Pruebas de acceso anónimo:** Intentar acceder a cada endpoint protegido sin token → debe retornar `401`.
2. **Pruebas de escalación:** Usuario no-admin intenta modificar `priv_admin` → debe retornar `403`.
3. **Pruebas de upload:** Subir archivo `.php` con extensión `.jpg` → debe ser rechazado.
4. **Prueba de fuerza bruta:** 10 intentos consecutivos de login fallido → debe activarse rate limit.
5. **Inspección de headers:** Verificar con `curl -I` que los headers de seguridad están presentes en producción.
6. **Verificación de Swagger:** En producción, `/docs` y `/redoc` no deben ser accesibles.

---

> **Nota:** Este plan se puede ejecutar de forma incremental. Se recomienda empezar por la **Etapa 1** (críticas) y hacer un commit/deploy antes de continuar con las siguientes etapas.
