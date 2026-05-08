from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep, CurrentUser, require_permission
from app.models.config import Config
from app.schemas.config import ConfigCreate, ConfigUpdate, ConfigRead

router = APIRouter(prefix="/api/v1/config", tags=["config"])


@router.get("/", response_model=list[ConfigRead], dependencies=[Depends(require_permission("settings", "priv_access"))])
async def get_all_config(session: SessionDep):
    result = await session.execute(select(Config))
    return result.scalars().all()


@router.get("/{key}", response_model=ConfigRead, dependencies=[Depends(require_permission("settings", "priv_access"))])
async def get_config(key: str, session: SessionDep):
    result = await session.execute(select(Config).where(Config.key == key))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return config


@router.post("/", response_model=ConfigRead, status_code=201, dependencies=[Depends(require_permission("settings", "priv_insert"))])
async def create_config(obj: ConfigCreate, session: SessionDep, current_user: CurrentUser):
    config = Config.model_validate(obj)
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config


@router.put("/{key}", response_model=ConfigRead, dependencies=[Depends(require_permission("settings", "priv_update"))])
async def update_config(key: str, obj: ConfigUpdate, session: SessionDep, current_user: CurrentUser):
    result = await session.execute(select(Config).where(Config.key == key))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    update_data = obj.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await session.commit()
    await session.refresh(config)
    return config


@router.delete("/{key}", dependencies=[Depends(require_permission("settings", "priv_delete"))])
async def delete_config(key: str, session: SessionDep, current_user: CurrentUser):
    result = await session.execute(select(Config).where(Config.key == key))
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    await session.delete(config)
    await session.commit()
    return {"message": "Configuración eliminada"}