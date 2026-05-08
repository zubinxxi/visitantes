from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep, CurrentUser
from app.models.security import SecUser, SecUserGroupLink, SecGroup
from app.schemas.security import SecGroupRead

router = APIRouter(prefix="/api/v1/security", tags=["security"])


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


@router.post("/groups/{group_id}/users/{user_login}", status_code=201)
async def add_user_to_group(group_id: int, user_login: str, session: SessionDep, current_user: CurrentUser):
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
