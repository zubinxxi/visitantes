# Visitantes AMP Backend

API REST para el sistema de gestión de visitantes de la Autoridad de los Asuntos de Indígenas (AAPI). Construido con **FastAPI**, **SQLModel** y **MariaDB**.

## Características

- Autenticación JWT con bcrypt (rounds=12)
- Control de permisos granular por grupo/aplicación (`sec_groups_apps`)
- CRUD completo generado programáticamente para tablas de mantenimiento
- Check-in/Check-out de visitantes con flujo QR
- Parseo de QR de cédulas panameñas
- Upload de fotos (subida temporal y vinculada a visitante)
- Recuperación de contraseña por correo SMTP
- Auditoría de operaciones (tabla `sc_log`)
- Rate limiting por endpoint (slowapi)
- Middleware de seguridad HTTP (HSTS, CSP headers)
- Migraciones con Alembic
- Zona horaria: `America/Panama`
- Documentación OpenAPI automática

## Requisitos

- Python 3.10+
- MariaDB/MySQL
- pip

## Instalación

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Copiar y editar el archivo de variables de entorno:

```bash
cp .env.example .env
```

Editar `.env`:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=visitorsdb
DB_USER=your_db_user
DB_PASS=your_db_password

# JWT
SECRET_KEY=change-me-to-a-secure-random-string
ADMIN_GROUP_ID=1
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Pool de conexiones
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=10
DB_POOL_RECYCLE=300

# Correo SMTP (recuperación de contraseña)
SMTP_TLS=true
SMTP_SSL=false
SMTP_PORT=587
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=info@visitantesdb.com
EMAILS_FROM_NAME="Visitantes AMP"

# Frontend
FRONTEND_HOST=http://localhost:5173

# Opcionales
DEBUG=false
PHOTOS_DIR=./photos/visitors
```

> Las variables `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS` y `SECRET_KEY` son obligatorias; sin ellas el sistema no arranca.

## Base de Datos

### Ejecutar migraciones

```bash
source .venv/bin/activate
PYTHONPATH=. alembic -c alembic.ini upgrade head
```

### Migraciones actuales

| Revisión | Descripción |
|----------|-------------|
| `001_add_visits_buildings` | Crea tabla pivote `visits_buildings` |
| `002_register_apps` | Inserta 6 aplicaciones base en `sec_apps` |
| `003_add_config_table` | Crea tabla `config` |
| `9854d513fdc6` | Crea tabla de auditoría `sc_log` |
| `004_seed_granular_apps_permissions` | Inserta 17 apps granulares y permisos para grupos 2, 3, 4 |

### Crear nueva migración

```bash
PYTHONPATH=. alembic -c alembic.ini revision -m "descripcion_cambio" --autogenerate
```

### Revertir migración

```bash
PYTHONPATH=. alembic -c alembic.ini downgrade -1
```

## Servidor

### Desarrollo

```bash
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Producción

```bash
PYTHONPATH=. uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

## Documentación API

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | ReDoc documentación |
| `http://localhost:8000/openapi.json` | Esquema OpenAPI |

## Autenticación

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"sysadmin","password":"123456"}'
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "login": "sysadmin",
    "name": "Administrador",
    "email": "oit.desarrollo@amp.gob.pa",
    "priv_admin": "Y"
  },
  "permissions": [
    {
      "group_id": 1,
      "app_name": "visitors",
      "priv_access": "Y",
      "priv_insert": "Y",
      "priv_delete": "Y",
      "priv_update": "Y",
      "priv_export": "Y",
      "priv_print": "Y"
    }
  ]
}
```

### Usar token en requests

```bash
curl http://localhost:8000/api/v1/visitors/ \
  -H "Authorization: Bearer eyJhbGci..."
```

## Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Inicio de sesión → JWT + permisos |
| `POST` | `/api/v1/auth/forgot-password` | Solicitar restablecimiento de contraseña (rate limit: 3/h) |
| `POST` | `/api/v1/auth/reset-password` | Restablecer contraseña con token |
| `POST` | `/api/v1/auth/change-password` | Cambiar contraseña (requiere auth) |

### Visitantes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visitors/` | Listar todos (paginado) |
| `GET` | `/api/v1/visitors/{id}` | Por ID |
| `GET` | `/api/v1/visitors/cedula/{cedula}` | Por cédula |
| `POST` | `/api/v1/visitors/` | Crear |
| `PUT` | `/api/v1/visitors/{id}` | Actualizar |
| `DELETE` | `/api/v1/visitors/{id}` | Eliminar |
| `POST` | `/api/v1/visitors/upload-photo-temp` | Subir foto temporal (antes de crear visitante) |
| `POST` | `/api/v1/visitors/{visitor_id}/upload-photo` | Subir foto a visitante existente |

### Visitas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visits/` | Listar todas |
| `GET` | `/api/v1/visits/paginated` | Listado paginado con filtros |
| `GET` | `/api/v1/visits/active` | Activas (sin checkout) |
| `GET` | `/api/v1/visits/export` | Exportar visitas |
| `GET` | `/api/v1/visits/stats/summary` | Estadísticas del dashboard |
| `POST` | `/api/v1/visits/checkin` | Check-in completo |
| `POST` | `/api/v1/visits/{id}/checkout` | Check-out individual |
| `POST` | `/api/v1/visits/checkout-by-qr` | Check-out mediante QR |
| `PATCH` | `/api/v1/visits/{visit_id}` | Actualizar (parcial) |
| `DELETE` | `/api/v1/visits/{id}` | Eliminar |

### Check-in

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/checkin/process-qr` | Procesar QR de cédula y buscar/crear visitante |
| `POST` | `/api/v1/checkin/register` | Registrar nuevo visitante + check-in |
| `POST` | `/api/v1/checkin/confirm` | Confirmar check-in con UADMs y edificios |
| `GET` | `/api/v1/checkin/visits/{visit_id}/badge` | Obtener datos para gafete |

### QR

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/qr/parse` | Parsear cédula panameña desde QR |

### Configuración

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/config/` | Listar configuraciones |
| `GET` | `/api/v1/config/{key}` | Obtener configuración por clave |
| `POST` | `/api/v1/config/` | Crear configuración |
| `PUT` | `/api/v1/config/{key}` | Actualizar configuración |
| `DELETE` | `/api/v1/config/{key}` | Eliminar configuración |

### Seguridad

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/security/me/permissions` | Permisos del usuario autenticado |
| `GET` | `/api/v1/security/groups` | Grupos del usuario autenticado |
| `GET` | `/api/v1/security/groups/{group_id}/users` | Usuarios por grupo |
| `POST` | `/api/v1/security/groups/{group_id}/users/{user_login}` | Agregar usuario a grupo |
| `DELETE` | `/api/v1/security/groups/{group_id}/users/{user_login}` | Eliminar usuario de grupo |
| `POST` | `/api/v1/security/permissions/upsert` | Crear o actualizar permiso |

### Health

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check (estado BD) |

### Mantenimiento

CRUD completo (`GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`) con permisos granulares:

| Prefijo | Tabla | appName |
|---------|-------|---------|
| `/api/v1/maintenance/provinces/` | Provincias | `maint_provinces` / `visitors` |
| `/api/v1/maintenance/institutions/` | Instituciones | `maint_institutions` |
| `/api/v1/maintenance/type_uadms/` | Tipos UADM | `maint_type_uadm` |
| `/api/v1/maintenance/buildings/` | Edificios | `maint_buildings` |
| `/api/v1/maintenance/procedures/` | Procedimientos | `maint_procedures` |
| `/api/v1/maintenance/uadms/` | Unidades administrativas | `maint_uadms` |
| `/api/v1/maintenance/groups/` | Grupos de seguridad | `sec_groups` |
| `/api/v1/maintenance/apps/` | Aplicaciones | `sec_apps` |
| `/api/v1/maintenance/group_apps/` | Permisos grupo-app | `sec_permissions` / `visitors` |
| `/api/v1/maintenance/users/` | Usuarios del sistema | `sec_users` |

## Usuarios por Defecto

| Login | Password | Rol |
|-------|----------|-----|
| sysadmin | 123456 | Administrador (priv_admin) |
| admindemo | 123456 | Admin Demo |
| usuariodemo | 123456 | Usuario Demo |
| ajimenez | 123456 | Admin |
| dmedina | 123456 | Admin |
| jarrue | 123456 | Admin |
| zjuarez | 123456 | Admin |

## Modelo de Permisos

```
sec_users → sec_users_groups → sec_groups → sec_groups_apps → sec_apps
```

Cada fila en `sec_groups_apps` define 6 privilegios:

| Privilegio | Descripción |
|------------|-------------|
| `priv_access` | Acceso a la aplicación |
| `priv_insert` | Crear registros |
| `priv_update` | Modificar registros |
| `priv_delete` | Eliminar registros |
| `priv_export` | Exportar datos |
| `priv_print` | Imprimir |

Los CRUD de mantenimiento aceptan múltiples `appName` (ej. `maint_provinces` o `visitors`), permitiendo que administradores con permiso general `visitors` también accedan a ellos.

## Rate Limiting

| Endpoint | Límite |
|----------|--------|
| `/api/v1/auth/login` | 5 intentos/minuto |
| `/api/v1/auth/forgot-password` | 3 intentos/hora |
| Global demás endpoints | 60/minuto |

## Seguridad HTTP

El middleware `SecurityHeadersMiddleware` agrega las siguientes cabeceras a todas las respuestas:

| Cabecera | Valor |
|----------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(self), microphone=()` |
| `Strict-Transport-Security` | `max-age=31536000` (solo HTTPS) |

## Auditoría

Las operaciones de escritura (check-in, checkout, creación de visitantes) se registran automáticamente en la tabla `sc_log` con: usuario, acción, timestamp, IP, y datos relevantes de la operación.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                    # Dependencias (SessionDep, CurrentUser)
│   │   └── v1/
│   │       ├── auth.py                # Login JWT, recuperación de contraseña
│   │       ├── checkin.py             # Flujo QR + registro + confirmación
│   │       ├── config.py              # CRUD configuraciones del sistema
│   │       ├── maintenance.py         # CRUD genérico programático
│   │       ├── qr.py                  # Parseo de QR
│   │       ├── security.py            # Permisos, grupos, miembros
│   │       ├── visitors.py            # CRUD visitantes + fotos
│   │       └── visits.py              # CRUD visitas, estadísticas, exportación
│   ├── core/
│   │   ├── config.py                  # Configuración (Settings + dotenv)
│   │   ├── emails.py                  # Envío de correos SMTP
│   │   ├── security.py                # bcrypt, JWT, hash/verify
│   │   └── utils.py                   # Utilidades (zona horaria, etc.)
│   ├── models/
│   │   ├── config.py                  # Modelo Config (tabla config)
│   │   ├── maintenance.py             # Province, Institution, TypeUadm, Building, etc.
│   │   ├── security.py                # SecGroup, SecApp, SecUser, SecGroupApp
│   │   ├── visit.py                   # Visit, VisitsUadmLink, VisitsBuildingsLink
│   │   └── visitor.py                 # Visitor (tabla visitors)
│   ├── schemas/
│   │   ├── config.py                  # Schemas Create/Read/Update para Config
│   │   ├── maintenance.py             # Schemas para tablas de mantenimiento
│   │   ├── security.py                # Schemas para auth, usuarios, permisos
│   │   ├── visit.py                   # Schemas para visitas, estadísticas
│   │   └── visitor.py                 # Schemas para visitantes
│   ├── services/
│   │   ├── audit_service.py           # Modelo ScLog + registro de auditoría
│   │   └── qr_service.py              # Parseo de QR de cédula panameña
│   ├── database.py                    # Engine asíncrono (asyncmy) + session
│   └── main.py                        # App FastAPI (routers, middleware, CORS)
├── alembic/                           # Migraciones
│   └── versions/                      # 5 migraciones
├── photos/visitors/                   # Fotos de visitantes
├── .env                               # Variables de entorno (NO commitear)
├── .env.example                       # Plantilla con todas las variables
├── .gitignore
├── alembic.ini
└── requirements.txt
```

## Tecnologías

| Componente | Versión |
|------------|---------|
| FastAPI | 0.115.6 |
| SQLModel | 0.0.22 |
| SQLAlchemy | 2.0.49 |
| Pydantic | 2.10.4 |
| asyncmy | 0.2.10 |
| bcrypt | 4.2.1 |
| Alembic | 1.14.1 |
| PyJWT | >=2.8.0 |
| slowapi | 0.1.9 |
| Uvicorn | 0.34.0 |

## Pruebas

### Health check

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","db":"visitorsdb"}
```

### Pruebas manuales

```bash
python test_backend.py
python check_db.py
```
