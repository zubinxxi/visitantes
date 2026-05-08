from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, APIRouter, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.database import get_session, async_engine
from app.api.deps import SessionDep
from app.api.v1 import auth, visitors, visits, qr, checkin, config, security
from app.api.v1.maintenance import MaintenanceCRUD, PaginatedResponse
from app.models.maintenance import (
    Province, Institution, TypeUadm, Building, TypeOfProcedure, Uadm,
)
from app.models.security import SecGroup, SecApp, SecGroupApp
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
from app.models.security import SecUser
from app.core.security import hash_password
 

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    async with async_engine.begin() as conn:
        pass
    yield
    # Shutdown
    await async_engine.dispose()


app = FastAPI(
    title="visitorsdb",
    description="Sistema de Gestión de Visitantes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

photos_dir = Path(settings.PHOTOS_DIR)
photos_dir.mkdir(parents=True, exist_ok=True)
app.mount("/photos/visitors", StaticFiles(directory=str(photos_dir)), name="photos")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(visitors.router, prefix="/api/v1")
app.include_router(visits.router, prefix="/api/v1")
app.include_router(qr.router, prefix="/api/v1")
app.include_router(checkin.router, prefix="/api/v1")


def build_crud_router(prefix: str, crud: MaintenanceCRUD, read_model, create_schema, update_schema, search_fields: list[str] = None):
    router = APIRouter(prefix=f"/api/v1/maintenance/{prefix}", tags=[f"maintenance-{prefix}"])

    @router.get("/", response_model=PaginatedResponse)
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

    @router.get("/{item_id}", response_model=read_model)
    async def get_by_id(session: SessionDep, item_id: int):
        return await crud.get_by_id(session, item_id)

    @router.post("/", response_model=read_model, status_code=201)
    async def create_item(session: SessionDep, obj: create_schema = Body()):
        return await crud.create(session, obj)

    @router.put("/{item_id}", response_model=read_model)
    async def update_item(session: SessionDep, item_id: int, obj: update_schema = Body()):
        return await crud.update(session, item_id, obj)

    @router.delete("/{item_id}")
    async def delete_item(session: SessionDep, item_id: int):
        return await crud.delete(session, item_id)

    return router


maintenance_configs = [
    ("provinces", Province, ProvinceCreate, ProvinceUpdate, ProvinceRead, ["description"]),
    ("institutions", Institution, InstitutionCreate, InstitutionUpdate, InstitutionRead, ["description"]),
    ("type_uadms", TypeUadm, TypeUadmCreate, TypeUadmUpdate, TypeUadmRead, ["description"]),
    ("buildings", Building, BuildingCreate, BuildingUpdate, BuildingRead, ["description"]),
    ("procedures", TypeOfProcedure, TypeOfProcedureCreate, TypeOfProcedureUpdate, TypeOfProcedureRead, ["description"]),
    ("uadms", Uadm, UadmCreate, UadmUpdate, UadmRead, ["name", "initials", "province_name", "institution_name", "type_uadm_name"]),
    ("groups", SecGroup, SecGroupCreate, SecGroupUpdate, SecGroupRead, ["description"]),
    ("apps", SecApp, SecAppCreate, SecAppUpdate, SecAppRead, ["name", "description"]),
    ("group_apps", SecGroupApp, SecGroupAppCreate, SecGroupAppUpdate, SecGroupAppRead, ["app_name"]),
]

for prefix, model, create_s, update_s, read_s, search_fields in maintenance_configs:
    crud = MaintenanceCRUD(model, create_s, update_s, read_s)
    router = build_crud_router(prefix, crud, read_s, create_s, update_s, search_fields)
    app.include_router(router)


users_crud = MaintenanceCRUD(SecUser, SecUserCreate, SecUserUpdate, SecUserRead)
users_router = APIRouter(prefix="/api/v1/maintenance/users", tags=["maintenance-users"])


@users_router.get("/", response_model=PaginatedResponse)
async def get_all_users(
    session: SessionDep,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=1000, description="Registros por página"),
    search: str = Query(None, description="Texto de búsqueda"),
):
    return await users_crud.get_all(session, page=page, limit=limit, search=search, search_fields=["login", "name", "email"])

@users_router.get("/{item_id}", response_model=SecUserRead)
async def get_user_by_id(session: SessionDep, item_id: str):
    return await users_crud.get_by_id(session, item_id)

@users_router.post("/", response_model=SecUserRead, status_code=201)
async def create_user(session: SessionDep, obj: SecUserCreate):
    obj_data = obj.model_dump()
    obj_data["pswd"] = hash_password(obj.pswd)
    return await users_crud.create(session, SecUserCreate(**obj_data))

@users_router.put("/{item_id}", response_model=SecUserRead)
async def update_user(session: SessionDep, item_id: str, obj: SecUserUpdate):
    update_data = obj.model_dump(exclude_unset=True)
    if "pswd" in update_data and update_data["pswd"]:
        update_data["pswd"] = hash_password(update_data["pswd"])
    return await users_crud.update(session, item_id, SecUserUpdate(**update_data))

@users_router.delete("/{item_id}")
async def delete_user(session: SessionDep, item_id: str):
    return await users_crud.delete(session, item_id)


app.include_router(users_router)
app.include_router(config.router)
app.include_router(security.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "db": "visitorsdb"}
