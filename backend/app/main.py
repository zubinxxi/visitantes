from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, APIRouter, Query, Body, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.database import get_session, async_engine
from app.api.deps import SessionDep, CurrentUser, require_permission, get_user_group_ids, is_user_admin
from app.api.v1 import auth, visitors, visits, qr, checkin, config, security
from app.api.v1.maintenance import MaintenanceCRUD, PaginatedResponse
from app.models.maintenance import (
    Province, Institution, TypeUadm, Building, TypeOfProcedure, Uadm,
)
from app.models.security import SecGroup, SecApp, SecGroupApp, SecUser, SecUserGroupLink
from app.schemas.maintenance import (
    ProvinceCreate, ProvinceRead, ProvinceUpdate,
    InstitutionCreate, InstitutionRead, InstitutionUpdate,
    TypeUadmCreate, TypeUadmRead, TypeUadmUpdate,
    BuildingCreate, BuildingRead, BuildingUpdate,
    TypeOfProcedureCreate, TypeOfProcedureRead, TypeOfProcedureUpdate,
    UadmCreate, UadmRead, UadmUpdate,
)
from app.schemas.security import (
    SecGroupCreate, SecGroupRead, SecGroupUpdate,
    SecAppCreate, SecAppRead, SecAppUpdate,
    SecGroupAppCreate, SecGroupAppRead, SecGroupAppUpdate,
    SecUserCreate, SecUserRead, SecUserUpdate,
)
from app.core.security import hash_password
from sqlmodel import select
 

# ID del grupo Administrador (desde configuración)
ADMIN_GROUP_ID = settings.ADMIN_GROUP_ID


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    async with async_engine.begin() as conn:
        pass
    yield
    # Shutdown
    await async_engine.dispose()


# ── Rate Limiter ──
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="visitorsdb",
    description="Sistema de Gestión de Visitantes",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Registrar rate limiter en el estado de la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS restringido ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_HOST,
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Middleware de Headers de Seguridad HTTP ──
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=()"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

photos_dir = Path(settings.PHOTOS_DIR)
photos_dir.mkdir(parents=True, exist_ok=True)
app.mount("/photos/visitors", StaticFiles(directory=str(photos_dir)), name="photos")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(visitors.router, prefix="/api/v1")
app.include_router(visits.router, prefix="/api/v1")
app.include_router(qr.router, prefix="/api/v1")
app.include_router(checkin.router, prefix="/api/v1")


def build_crud_router(
    prefix: str,
    crud: MaintenanceCRUD,
    read_model,
    create_schema,
    update_schema,
    search_fields: list[str] = None,
    app_name: str | list[str] = None,
):
    router = APIRouter(prefix=f"/api/v1/maintenance/{prefix}", tags=[f"maintenance-{prefix}"])

    # Si app_name es lista, el primero es el principal (CRUD completo), 
    # los demás son solo para lectura (access).
    primary_app = app_name[0] if isinstance(app_name, list) else app_name
    read_apps = app_name if isinstance(app_name, list) else [app_name] if app_name else []

    # Dependencia de permiso según el app_name
    access_dep = Depends(require_permission(read_apps, "priv_access")) if read_apps else None
    insert_dep = Depends(require_permission(primary_app, "priv_insert")) if primary_app else None
    update_dep = Depends(require_permission(primary_app, "priv_update")) if primary_app else None
    delete_dep = Depends(require_permission(primary_app, "priv_delete")) if primary_app else None

    deps_get = [access_dep] if access_dep else []
    deps_post = [insert_dep] if insert_dep else []
    deps_put = [update_dep] if update_dep else []
    deps_del = [delete_dep] if delete_dep else []

    @router.get("/", response_model=PaginatedResponse, dependencies=deps_get)
    async def get_all(
        session: SessionDep,
        page: int = Query(1, ge=1, description="Número de página"),
        limit: int = Query(10, ge=1, le=1000, description="Registros por página"),
        search: str = Query(None, description="Texto de búsqueda"),
    ):
        return await crud.get_all(
            session, 
            page=page, 
            limit=limit, 
            search=search if search else None,
            search_fields=search_fields,
        )

    @router.get("/{item_id}", response_model=read_model, dependencies=deps_get)
    async def get_by_id(session: SessionDep, item_id: int):
        return await crud.get_by_id(session, item_id)

    @router.post("/", response_model=read_model, status_code=201, dependencies=deps_post)
    async def create_item(session: SessionDep, obj: create_schema = Body()):
        return await crud.create(session, obj)

    @router.put("/{item_id}", response_model=read_model, dependencies=deps_put)
    async def update_item(session: SessionDep, item_id: int, obj: update_schema = Body()):
        return await crud.update(session, item_id, obj)

    @router.delete("/{item_id}", dependencies=deps_del)
    async def delete_item(session: SessionDep, item_id: int):
        return await crud.delete(session, item_id)

    return router


# Configuración de CRUDs de mantenimiento con sus app_names granulares
maintenance_configs = [
    ("provinces", Province, ProvinceCreate, ProvinceUpdate, ProvinceRead, ["description"], ["maint_provinces", "visitors"]),
    ("institutions", Institution, InstitutionCreate, InstitutionUpdate, InstitutionRead, ["description"], "maint_institutions"),
    ("type_uadms", TypeUadm, TypeUadmCreate, TypeUadmUpdate, TypeUadmRead, ["description"], "maint_type_uadm"),
    ("buildings", Building, BuildingCreate, BuildingUpdate, BuildingRead, ["description"], ["maint_buildings", "visitors"]),
    ("procedures", TypeOfProcedure, TypeOfProcedureCreate, TypeOfProcedureUpdate, TypeOfProcedureRead, ["description"], "maint_procedures"),
    ("uadms", Uadm, UadmCreate, UadmUpdate, UadmRead, ["name", "initials", "province_name", "institution_name", "type_uadm_name"], ["maint_uadms", "visitors"]),
    ("groups", SecGroup, SecGroupCreate, SecGroupUpdate, SecGroupRead, ["description"], ["sec_groups", "sec_users"]),
    ("apps", SecApp, SecAppCreate, SecAppUpdate, SecAppRead, ["name", "description"], "sec_apps"),
    ("group_apps", SecGroupApp, SecGroupAppCreate, SecGroupAppUpdate, SecGroupAppRead, ["app_name"], "sec_permissions"),
]

for prefix, model, create_s, update_s, read_s, search_fields, perm_app in maintenance_configs:
    crud = MaintenanceCRUD(model, create_s, update_s, read_s)
    router = build_crud_router(prefix, crud, read_s, create_s, update_s, search_fields, app_name=perm_app)
    app.include_router(router)


# ── CRUD de Usuarios (con protección especial Admin-Seguridad) ──

users_crud = MaintenanceCRUD(SecUser, SecUserCreate, SecUserUpdate, SecUserRead)
users_router = APIRouter(prefix="/api/v1/maintenance/users", tags=["maintenance-users"])


async def _check_target_is_admin(session, target_login: str) -> bool:
    """Verifica si el usuario destino pertenece al grupo Administrador."""
    result = await session.execute(
        select(SecUserGroupLink.group_id).where(
            SecUserGroupLink.login == target_login,
            SecUserGroupLink.group_id == ADMIN_GROUP_ID,
        )
    )
    return result.first() is not None


@users_router.get(
    "/",
    response_model=PaginatedResponse,
    dependencies=[Depends(require_permission("sec_users", "priv_access"))],
)
async def get_all_users(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=1000, description="Registros por página"),
    search: str = Query(None, description="Texto de búsqueda"),
):
    return await users_crud.get_all(session, page=page, limit=limit, search=search, search_fields=["login", "name", "email"])

@users_router.get(
    "/{item_id}",
    response_model=SecUserRead,
    dependencies=[Depends(require_permission("sec_users", "priv_access"))],
)
async def get_user_by_id(session: SessionDep, item_id: str):
    return await users_crud.get_by_id(session, item_id)

@users_router.post(
    "/",
    response_model=SecUserRead,
    status_code=201,
)
async def create_user(
    session: SessionDep,
    obj: SecUserCreate,
    current_user: SecUser = Depends(require_permission("sec_users", "priv_insert")),
):
    obj_data = obj.model_dump()
    
    # Prevenir escalación de priv_admin
    if obj_data.get("priv_admin") == "Y":
        if not await is_user_admin(session, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para crear usuarios con privilegios de Administrador",
            )

    obj_data["pswd"] = hash_password(obj.pswd)
    return await users_crud.create(session, SecUserCreate(**obj_data))

@users_router.put(
    "/{item_id}",
    response_model=SecUserRead,
)
async def update_user(
    session: SessionDep,
    item_id: str,
    obj: SecUserUpdate,
    current_user: SecUser = Depends(require_permission("sec_users", "priv_update")),
):
    # Admin-Seguridad no puede editar usuarios del grupo Administrador
    if not await is_user_admin(session, current_user):
        if await _check_target_is_admin(session, item_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para editar usuarios del grupo Administrador",
            )
        
        # Prevenir escalación: Admin-Seguridad no puede asignar priv_admin='Y'
        if obj.priv_admin == "Y":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para asignar privilegios de Administrador",
            )

    update_data = obj.model_dump(exclude_unset=True)
    if "pswd" in update_data and update_data["pswd"]:
        update_data["pswd"] = hash_password(update_data["pswd"])
    return await users_crud.update(session, item_id, SecUserUpdate(**update_data))

@users_router.delete("/{item_id}")
async def delete_user(
    session: SessionDep,
    item_id: str,
    current_user: SecUser = Depends(require_permission("sec_users", "priv_delete")),
):
    # Admin-Seguridad no puede eliminar usuarios del grupo Administrador
    if not await is_user_admin(session, current_user):
        if await _check_target_is_admin(session, item_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para eliminar usuarios del grupo Administrador",
            )
    return await users_crud.delete(session, item_id)


app.include_router(users_router)
app.include_router(config.router)
app.include_router(security.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "db": "visitorsdb"}
