---
name: sc-security-module
description: Módulo de seguridad RBAC standalone para proyectos FastAPI + SQLModel + Frontend Vue.
---

# Módulo de Seguridad SC/SEC — RBAC Granular

Módulo **standalone** de permisos basado en roles (RBAC). Solo requiere sus 6 tablas — cero dependencias del negocio. Incluye esquema de BD, backend FastAPI, stores frontend y protección de rutas/acciones.

## 1. Tablas del Módulo

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# --- Usuarios ---
class SecUser(SQLModel, table=True):
    __tablename__ = "sec_users"
    login: str = Field(primary_key=True, max_length=255)
    pswd: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    active: Optional[str] = Field(default=None, max_length=1)
    activation_code: Optional[str] = Field(default=None, max_length=32)
    priv_admin: Optional[str] = Field(default=None, max_length=1)
    mfa: Optional[str] = Field(default=None, max_length=255)
    picture: Optional[bytes] = None
    role: Optional[str] = Field(default=None, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=64)
    pswd_last_updated: Optional[datetime] = None
    mfa_last_updated: Optional[datetime] = None

# --- Grupos ---
class SecGroup(SQLModel, table=True):
    __tablename__ = "sec_groups"
    group_id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, max_length=255)

# --- Relación Usuario-Grupo (N:M) ---
class SecUserGroupLink(SQLModel, table=True):
    __tablename__ = "sec_users_groups"
    login: str = Field(primary_key=True, foreign_key="sec_users.login")
    group_id: int = Field(primary_key=True, foreign_key="sec_groups.group_id")

# --- Aplicaciones/Módulos ---
class SecApp(SQLModel, table=True):
    __tablename__ = "sec_apps"
    app_name: str = Field(primary_key=True, max_length=128)
    app_type: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)

# --- Permisos (clave compuesta group_id + app_name) ---
class SecGroupApp(SQLModel, table=True):
    __tablename__ = "sec_groups_apps"
    group_id: int = Field(primary_key=True, foreign_key="sec_groups.group_id")
    app_name: str = Field(primary_key=True, foreign_key="sec_apps.app_name")
    priv_access: Optional[str] = Field(default=None, max_length=1)
    priv_insert: Optional[str] = Field(default=None, max_length=1)
    priv_delete: Optional[str] = Field(default=None, max_length=1)
    priv_update: Optional[str] = Field(default=None, max_length=1)
    priv_export: Optional[str] = Field(default=None, max_length=1)
    priv_print: Optional[str] = Field(default=None, max_length=1)

# --- Auditoría ---
class ScLog(SQLModel, table=True):
    __tablename__ = "sc_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    inserted_date: Optional[datetime] = Field(default=None)
    username: str = Field(max_length=90)
    application: str = Field(max_length=255)
    action: str = Field(max_length=30)
    ip_user: str = Field(max_length=255)
    description: Optional[str] = None
```

### Privilegios (columna `Optional[str]`, valor `"Y"` / `"N"` / `None`)

| Privilegio | Descripción |
|------------|-------------|
| `priv_access` | Ver la página/módulo |
| `priv_insert` | Crear registros |
| `priv_update` | Editar registros |
| `priv_delete` | Eliminar registros |
| `priv_export` | Exportar datos |
| `priv_print` | Imprimir |

### Grupos por defecto

| group_id | Descripción |
|----------|-------------|
| 1 | Administrador (permisos implícitos — no necesita registros en `sec_groups_apps`) |
| * | El resto se define por proyecto: `Usuarios`, `Seguridad`, `Admin-Seguridad`, etc. |

## 2. Backend — Core de Seguridad

### Config (`core/config.py`)

```python
SECRET_KEY: str                    # HMAC para JWT
ADMIN_GROUP_ID: int = 1            # grupo con permisos implícitos
ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
```

### Core Security (`core/security.py`)

bcrypt rounds=12, JWT HS256, UTC-5.

```python
import bcrypt, hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    return hashlib.md5(plain.encode()).hexdigest() == hashed

def create_access_token(subject: str, name="", role="", expires_delta=None) -> str:
    expire = now_panama() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    if name: to_encode["name"] = name
    if role: to_encode["role"] = role
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> Optional[str]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"]).get("sub")
    except JWTError:
        return None

def create_password_reset_token(subject: str) -> str:
    expire = now_panama() + timedelta(minutes=15)
    return jwt.encode({"sub": subject, "exp": expire, "type": "password_reset"}, SECRET_KEY, algorithm="HS256")

def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub") if payload.get("type") == "password_reset" else None
    except JWTError:
        return None
```

### Timezone (`core/utils.py`)

```python
TIMEZONE_PANAMA = timezone(timedelta(hours=-5))

def now_panama() -> datetime:           # timezone-aware (para JWT)
    return datetime.now(TIMEZONE_PANAMA)

def now_panama_naive() -> datetime:     # naive (para columnas datetime de MariaDB)
    return datetime.now(TIMEZONE_PANAMA).replace(tzinfo=None)
```

### Dependencias (`api/deps.py`)

| Componente | Propósito |
|------------|-----------|
| `SessionDep` | `Annotated[AsyncSession, Depends(get_session)]` |
| `get_current_user` | Extrae Bearer token, decodifica, busca usuario activo |
| `get_current_user_optional` | Igual pero devuelve `None` si no hay token |
| `CurrentUser` | `Annotated[SecUser, Depends(get_current_user)]` |
| `require_permission(app_name, privilege)` | Factory. Admin bypass (priv_admin o grupo Admin). Consulta `sec_groups_apps`. Soporta `str \| list[str]`. Retorna 403 si no tiene permiso. |
| `is_user_admin(session, user)` | True si `priv_admin == "Y"` o pertenece al grupo Admin |

### Endpoints de Auth (`api/v1/auth.py`)

| Método | Ruta | Propósito |
|--------|------|-----------|
| `POST` | `/auth/login` | Login → token + usuario + group_ids + permisos |
| `POST` | `/auth/forgot-password` | Token 15min + email vía BackgroundTasks |
| `POST` | `/auth/reset-password` | Valida token, actualiza password |
| `POST` | `/auth/change-password` | Cambia password (requiere auth + password actual) |

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "login": "x", "name": "x", "email": "x", "priv_admin": "N", "role": "x" },
  "group_ids": [1, 2],
  "permissions": [ /* SecGroupApp serializados */ ]
}
```

### Endpoints de Seguridad (`api/v1/security.py`)

| Método | Ruta | Propósito |
|--------|------|-----------|
| `POST` | `/security/permissions/upsert` | Crea o actualiza permiso (clave compuesta group_id+app_name) |
| `GET` | `/security/groups?login=x` | Grupos de un usuario |
| `GET` | `/security/groups/{id}/users` | Miembros de un grupo |
| `POST` | `/security/groups/{id}/users/{login}` | Agrega usuario a grupo |
| `DELETE` | `/security/groups/{id}/users/{login}` | Remueve usuario de grupo |
| `GET` | `/security/me/permissions` | Permisos consolidados del usuario autenticado |

### SMTP / Emails (`core/emails.py`)

Envío de correo transaccional con `smtplib`. Soporta TLS/SSL. Si `SMTP_HOST` no está configurado, logea warning sin crashear. Usar `BackgroundTasks` para no bloquear la respuesta.

## 3. Frontend — Stores

### Permissions Store (`stores/permissions.ts`)

Store Pinia con:
- **Estado**: `permissions[]`, `groupIds[]`, `privAdmin`
- **Persistencia en localStorage** con versionado
- **Computed `isAdmin`**: `privAdmin === 'Y' \|\| groupIds.includes(ADMIN_GROUP_ID)`
- **Métodos**: `setPermissions()`, `clearPermissions()`, `refreshPermissions()` (consume `GET /security/me/permissions`)
- **Helpers**: `hasAccess(appName)`, `canCreate()`, `canEdit()`, `canDelete()`, `canExport()`, `canPrint()`

### Auth Store (`stores/auth.ts`)

- `login()`: POST `/auth/login`, guarda token en localStorage, persiste permisos en `permissionsStore`
- `logout()`: limpia token + permisos
- `forgotPassword()`, `resetPassword()`, `changePassword()`: wrappers de fetch

### Axios Interceptor (`lib/api.ts`)

- Adjunta `Authorization: Bearer` automáticamente
- En 401: limpia localStorage y redirige a `/login`

## 4. Frontend — Protección de Rutas y UI

### Router Guard

Cada ruta protegida lleva `meta.appName`. El `beforeEach`:
1. Auth check → redirect a `/login`
2. Si tiene `appName` y no es admin → verifica `perms.hasAccess(appName)` → si no, redirect a homepage

### Sidebar

Cada ítem del menú tiene `appName`. `v-if="permissionsStore.hasAccess(item.appName)"`. Secciones enteras se ocultan si ningún ítem es visible.

### Acciones Condicionales

En tablas CRUD, botones condicionados:
- Nuevo → `canCreate(appName)`
- Editar → `canEdit(appName)`
- Eliminar → `canDelete(appName)`
- Exportar → `canExport(appName)`
- Imprimir → `canPrint(appName)`

## 5. Convenciones y Detalles

- **bcrypt rounds = 12**
- **JWT HS256**, claims: `sub` (login), `exp` (timezone-aware), `name`, `role`
- **Admin bypass**: no consulta BD de permisos si `priv_admin == "Y"` o pertenece al grupo Admin configurado
- **ScLog**: capturar usuario, acción, app, IP, timestamp en cada operación crítica
- **Migraciones Alembic**: seed de apps y permisos vía migración
- **CORS**: configurar orígenes del frontend + localhost dev
