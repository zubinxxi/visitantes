# VisitorsDB Backend

API REST para el sistema de gestión de visitantes, construido con **FastAPI** y **SQLModel**.

## 🚀 Características

- Autenticación JWT con hash bcrypt
- Control de permisos por grupo/app (`sec_groups_apps`)
- CRUD completo para todas las tablas de mantenimiento
- Check-in/Check-out de visitantes
- Parseo de QR de cédulas panameñas
- Upload de fotos
- Migraciones con Alembic
- Documentación OpenAPI automática

## 📋 Requisitos

- Python 3.10+
- MariaDB/MySQL
- pip

## ⚡ Instalación

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

Copiar y editar el archivo de variables de entorno:

```bash
cp .env.example .env
```

Editar `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=visitorsdb
DB_USER=visitorsdb
DB_PASS=tu_password_aqui

SECRET_KEY=tu_clave_secreta_segura
ACCESS_TOKEN_EXPIRE_MINUTES=480

DEBUG=false
PHOTOS_DIR=./photos/visitors
```

> ⚠️ **Nunca commitear el archivo `.env`.** Ya está en `.gitignore`.

## 🗄️ Base de Datos

### Ejecutar migraciones

```bash
source .venv/bin/activate
PYTHONPATH=. alembic -c alembic.ini upgrade head
```

### Migración de contraseñas

Las contraseñas existentes en MD5 se migran a bcrypt:

```bash
mysql -u visitorsdb -p < sql/001_migrate_passwords.sql
```

## 🏃 Ejecutar Servidor

```bash
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Opciones de producción

```bash
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

## 📖 Documentación API

Una vez en ejecución:

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | ReDoc documentación |
| `http://localhost:8000/openapi.json` | Esquema OpenAPI |

## 🔐 Autenticación

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"sysadmin","password":"123456"}'
```

**Response:**

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

## 📡 Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Login → JWT + permisos |

### Visitantes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visitors/` | Listar todos |
| `GET` | `/api/v1/visitors/{id}` | Por ID |
| `GET` | `/api/v1/visitors/cedula/{cedula}` | Por cédula |
| `POST` | `/api/v1/visitors/` | Crear (requiere auth) |
| `PUT` | `/api/v1/visitors/{id}` | Actualizar |
| `DELETE` | `/api/v1/visitors/{id}` | Eliminar |
| `POST` | `/api/v1/visitors/upload-photo` | Subir foto |

### Visitas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/visits/` | Listar todas |
| `GET` | `/api/v1/visits/active` | Activas (sin checkout) |
| `GET` | `/api/v1/visits/{id}` | Por ID |
| `POST` | `/api/v1/visits/checkin` | Check-in completo |
| `POST` | `/api/v1/visits/{id}/checkout` | Check-out |
| `PUT` | `/api/v1/visits/{id}` | Actualizar |
| `DELETE` | `/api/v1/visits/{id}` | Eliminar |

### QR

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/qr/parse` | Parsear cédula panameña |

### Mantenimiento

CRUD completo (`GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`) para:

| Prefijo | Tabla |
|---------|-------|
| `/api/v1/maintenance/provinces/` | Provincias |
| `/api/v1/maintenance/institutions/` | Instituciones |
| `/api/v1/maintenance/type_uadms/` | Tipos UADM |
| `/api/v1/maintenance/buildings/` | Edificios |
| `/api/v1/maintenance/procedures/` | Procedimientos |
| `/api/v1/maintenance/uadms/` | Unidades administrativas |
| `/api/v1/maintenance/groups/` | Grupos de seguridad |
| `/api/v1/maintenance/apps/` | Aplicaciones |
| `/api/v1/maintenance/group_apps/` | Permisos |

## 🏗️ Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Dependencias (SessionDep, CurrentUser)
│   │   └── v1/
│   │       ├── auth.py             # Login JWT
│   │       ├── visitors.py         # CRUD visitantes
│   │       ├── visits.py           # CRUD visitas
│   │       ├── qr.py               # Parseo QR
│   │       └── maintenance.py      # CRUD genérico
│   ├── core/
│   │   ├── config.py               # Configuración (python-dotenv)
│   │   └── security.py             # bcrypt, JWT
│   ├── models/                     # SQLModel (tablas)
│   ├── schemas/                    # Pydantic (request/response)
│   ├── services/                   # Lógica de negocio
│   ├── database.py                 # Engine + session
│   └── main.py                     # App FastAPI
├── alembic/                        # Migraciones
├── photos/                         # Fotos de visitantes
├── .env                            # Variables (NO commitear)
├── .env.example                    # Plantilla
├── .gitignore
├── alembic.ini
└── requirements.txt
```

## 🧪 Pruebas

### Health check

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","db":"visitorsdb"}
```

### Ejemplo: Crear visitante

```bash
curl -X POST http://localhost:8000/api/v1/visitors/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "names": "Juan",
    "surnames": "Pérez",
    "gender": "M",
    "id_card_number": "8-745-1325",
    "id_num_control": "",
    "province": "Panamá",
    "nationality": "Panameño",
    "photo": "",
    "user_created": "sysadmin"
  }'
```

### Ejemplo: Check-in

```bash
curl -X POST http://localhost:8000/api/v1/visits/checkin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "names": "María",
    "surnames": "García",
    "gender": "F",
    "id_card_number": "4-123-456",
    "id_num_control": "",
    "province": "Colón",
    "nationality": "Panameño",
    "id_type_of_proce": 2,
    "company_represents": "",
    "purpose": "Reunión de trabajo",
    "uadm_ids": [1],
    "building_ids": [1],
    "user_created": "sysadmin"
  }'
```

## 👥 Usuarios por Defecto

| Login | Password | Rol |
|-------|----------|-----|
| sysadmin | 123456 | Administrador |
| admindemo | 123456 | Admin Demo |
| usuariodemo | 123456 | Usuario Demo |
| ajimenez | 123456 | Admin |
| dmedina | 123456 | Admin |
| jarrue | 123456 | Admin |
| zjuarez | 123456 | Admin |

## 🔒 Modelo de Permisos

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

## 📝 Migraciones

### Crear nueva migración

```bash
PYTHONPATH=. alembic -c alembic.ini revision -m "descripcion_cambio" --autogenerate
```

### Aplicar migraciones

```bash
PYTHONPATH=. alembic -c alembic.ini upgrade head
```

### Revertir migración

```bash
PYTHONPATH=. alembic -c alembic.ini downgrade -1
```

## 🛠️ Tecnologías

| Componente | Versión |
|------------|---------|
| FastAPI | 0.115.6 |
| SQLModel | 0.0.22 |
| SQLAlchemy | 2.0.49 |
| Pydantic | 2.10.4 |
| asyncmy | 0.2.10 |
| bcrypt | 4.2.1 |
| Alembic | 1.14.1 |
| Uvicorn | 0.34.0 |
