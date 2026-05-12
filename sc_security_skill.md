---
name: sc-security-module
description: Implementación completa del módulo de seguridad RBAC para proyectos FastAPI + Frontend.
---

# Módulo de Seguridad SC/SEC

Este skill proporciona la guía completa para implementar el sistema de seguridad basado en roles (RBAC) utilizado en el proyecto Visitantes AMP. Incluye la estructura de base de datos, lógica de backend en FastAPI y patrones de integración en el frontend.

## 1. Estructura de Base de Datos (SQLModel)

El módulo utiliza el prefijo `sec_` para tablas de seguridad y `sc_` para auditoría.

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# --- Usuarios ---
class SecUser(SQLModel, table=True):
    __tablename__ = "sec_users"
    login: str = Field(primary_key=True, max_length=255)
    pswd: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    active: str = Field(default="Y", max_length=1)
    priv_admin: str = Field(default="N", max_length=1)
    role: Optional[str] = Field(default=None, max_length=128)
    pswd_last_updated: Optional[datetime] = None

# --- Grupos ---
class SecGroup(SQLModel, table=True):
    __tablename__ = "sec_groups"
    group_id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=255)

# --- Relación Usuario-Grupo ---
class SecUserGroupLink(SQLModel, table=True):
    __tablename__ = "sec_users_groups"
    login: str = Field(primary_key=True, foreign_key="sec_users.login")
    group_id: int = Field(primary_key=True, foreign_key="sec_groups.group_id")

# --- Aplicaciones/Módulos ---
class SecApp(SQLModel, table=True):
    __tablename__ = "sec_apps"
    app_name: str = Field(primary_key=True, max_length=128)
    description: Optional[str] = None

# --- Permisos (RBAC) ---
class SecGroupApp(SQLModel, table=True):
    __tablename__ = "sec_groups_apps"
    group_id: int = Field(primary_key=True, foreign_key="sec_groups.group_id")
    app_name: str = Field(primary_key=True, foreign_key="sec_apps.app_name")
    priv_access: str = Field(default="N", max_length=1)
    priv_insert: str = Field(default="N", max_length=1)
    priv_delete: str = Field(default="N", max_length=1)
    priv_update: str = Field(default="N", max_length=1)
    priv_export: str = Field(default="N", max_length=1)
    priv_print: str = Field(default="N", max_length=1)

# --- Auditoría ---
class ScLog(SQLModel, table=True):
    __tablename__ = "sc_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    inserted_date: datetime = Field(default_factory=datetime.now)
    username: str = Field(max_length=90)
    application: str = Field(max_length=255)
    action: str = Field(max_length=30)
    ip_user: str = Field(max_length=255)
    description: Optional[str] = None
```

## 2. Lógica Core del Backend (FastAPI)

### Seguridad (`core/security.py`)
Utiliza `bcrypt` para passwords y `python-jose` para JWT.

```python
import bcrypt
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "tu_llave_secreta"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Dependencias (`api/deps.py`)
El corazón del RBAC es el `require_permission`.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.api.deps import SessionDep # Tu sesión de DB

security_scheme = HTTPBearer()

async def get_current_user(token: str = Depends(security_scheme), session: SessionDep):
    # Decodificar token y buscar usuario en SecUser
    # Validar que esté activo
    pass

def require_permission(app_name: str, privilege: str = "priv_access"):
    async def checker(user: SecUser = Depends(get_current_user), session: SessionDep):
        if user.priv_admin == "Y": return user
        # 1. Obtener IDs de grupos del usuario (SecUserGroupLink)
        # 2. Buscar en SecGroupApp si algún grupo tiene el privilegio en app_name
        # 3. Si no, lanzar HTTPException 403
        pass
    return checker
```

## 3. Integración en el Frontend (Store pattern)

### Gestión de Estado (Pinia/Redux)
El frontend debe almacenar el token y decodificar los permisos al iniciar sesión.

```javascript
// Ejemplo en Pinia (Vue)
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    permissions: [],
    isAdmin: false
  }),
  actions: {
    async login(credentials) {
      const { data } = await api.post('/auth/login', credentials);
      this.token = data.access_token;
      this.permissions = data.permissions; // Lista de objetos SecGroupApp
      this.isAdmin = data.user.priv_admin === 'Y';
      localStorage.setItem('token', this.token);
    },
    hasPermission(appName, privilege = 'priv_access') {
      if (this.isAdmin) return true;
      return this.permissions.some(p => p.app_name === appName && p[privilege] === 'Y');
    }
  }
});
```

### Directivas/Protección de Rutas
- **Rutas**: Usar un `Navigation Guard` que verifique `requiresAuth` y el permiso específico definido en la meta-data de la ruta.
- **Botones**: Ocultar botones o acciones si el usuario no tiene `priv_insert`, `priv_update` o `priv_delete`.

## 4. Endpoints Requeridos
- `POST /auth/login`: Retorna Token + Usuario + Permisos consolidados.
- `POST /auth/forgot-password`: Genera token temporal y envía email (SMTP).
- `POST /auth/reset-password`: Valida token y actualiza password.
- `POST /auth/change-password`: Cambia password (requiere auth).

## 5. Auditoría (sc_log)
Cada acción crítica (insert, update, delete) debe registrarse en la tabla `sc_log` capturando:
- Usuario que lo hizo.
- Acción realizada.
- Entidad/Aplicación afectada.
- IP del cliente.
- Fecha y hora (UTC-5 Panamá).
