from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep, CurrentUser, get_current_user, get_user_group_ids
from app.models.security import SecUser, SecUserGroupLink, SecGroup, SecGroupApp
from app.schemas.security import SecGroupRead, SecGroupAppRead, SecGroupAppCreate

router = APIRouter(prefix="/api/v1/security", tags=["security"])

# ID del grupo Administrador
ADMIN_GROUP_ID = 1


@router.post("/permissions/upsert", response_model=SecGroupAppRead)
async def upsert_permission(
    session: SessionDep,
    current_user: CurrentUser,
    obj_in: SecGroupAppCreate,
):
    """
    Crea o actualiza un permiso de aplicación para un grupo.
    Maneja la clave compuesta (group_id, app_name).
    """
    # Buscar registro existente
    result = await session.execute(
        select(SecGroupApp)
        .where(SecGroupApp.group_id == obj_in.group_id)
        .where(SecGroupApp.app_name == obj_in.app_name)
    )
    db_obj = result.scalars().first()

    if db_obj:
        # Actualizar campos existentes
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
    else:
        # Crear nuevo registro
        db_obj = SecGroupApp(**obj_in.model_dump())
        session.add(db_obj)

    await session.commit()
    await session.refresh(db_obj)
    return db_obj


@router.get("/groups", response_model=list[SecGroupRead])
async def get_groups_by_user(
    login: Annotated[str, Query(description="Login del usuario para obtener sus grupos")],
    session: SessionDep,
):
    user = await session.execute(select(SecUser).where(SecUser.login == login))
    if not user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario '{login}' no encontrado",
        )

    result = await session.execute(
        select(SecGroup)
        .join(SecUserGroupLink, SecGroup.group_id == SecUserGroupLink.group_id)
        .where(SecUserGroupLink.login == login)
    )
    return result.scalars().all()


@router.get("/groups/{group_id}/users", response_model=list[str])
async def get_users_by_group(group_id: int, session: SessionDep):
    result = await session.execute(
        select(SecUser.login)
        .join(SecUserGroupLink, SecUser.login == SecUserGroupLink.login)
        .where(SecUserGroupLink.group_id == group_id)
    )
    return result.scalars().all()


async def _check_admin_security_restriction(
    session: AsyncSession,
    current_user: SecUser,
    target_group_id: int,
):
    """
    Verifica que un usuario Admin-Seguridad no pueda modificar
    miembros del grupo Administrador.
    """
    current_group_ids = await get_user_group_ids(session, current_user.login)
    is_admin = current_user.priv_admin == "Y" or ADMIN_GROUP_ID in current_group_ids

    if not is_admin and target_group_id == ADMIN_GROUP_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para modificar miembros del grupo Administrador",
        )


@router.post("/groups/{group_id}/users/{user_login}", status_code=201)
async def add_user_to_group(group_id: int, user_login: str, session: SessionDep, current_user: CurrentUser):
    # Verificar restricción Admin-Seguridad
    await _check_admin_security_restriction(session, current_user, group_id)

    user_result = await session.execute(select(SecUser).where(SecUser.login == user_login))
    if not user_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    group_result = await session.execute(select(SecGroup).where(SecGroup.group_id == group_id))
    if not group_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")

    existing = await session.execute(
        select(SecUserGroupLink)
        .where(SecUserGroupLink.login == user_login)
        .where(SecUserGroupLink.group_id == group_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya pertenece al grupo")

    link = SecUserGroupLink(login=user_login, group_id=group_id)
    session.add(link)
    await session.commit()
    return {"message": "Usuario agregado al grupo"}


@router.delete("/groups/{group_id}/users/{user_login}")
async def remove_user_from_group(group_id: int, user_login: str, session: SessionDep, current_user: CurrentUser):
    # Verificar restricción Admin-Seguridad
    await _check_admin_security_restriction(session, current_user, group_id)

    result = await session.execute(
        select(SecUserGroupLink)
        .where(SecUserGroupLink.login == user_login)
        .where(SecUserGroupLink.group_id == group_id)
    )
    link = result.scalars().first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no está en el grupo")

    await session.delete(link)
    await session.commit()
    return {"message": "Usuario eliminado del grupo"}


@router.get("/me/permissions")
async def get_my_permissions(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Devuelve los permisos consolidados del usuario autenticado."""
    group_ids = await get_user_group_ids(session, current_user.login)

    permissions = []
    if group_ids:
        perms_result = await session.execute(
            select(SecGroupApp).where(SecGroupApp.group_id.in_(group_ids))
        )
        permissions = [
            SecGroupAppRead.model_validate(p).model_dump()
            for p in perms_result.scalars().all()
        ]

    return {
        "login": current_user.login,
        "priv_admin": current_user.priv_admin,
        "group_ids": list(group_ids),
        "permissions": permissions,
    }
