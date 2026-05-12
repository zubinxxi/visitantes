from typing import Annotated
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_session
from app.core.security import decode_access_token
from app.models.security import SecUser, SecGroupApp

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# ID del grupo Administrador
ADMIN_GROUP_ID = 1


async def get_current_user_optional(
    session: SessionDep,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[SecUser]:
    if credentials is None:
        return None
    
    token = credentials.credentials
    login = decode_access_token(token)
    
    if not login:
        return None
    
    result = await session.execute(select(SecUser).where(SecUser.login == login))
    user = result.scalars().first()
    
    if not user or user.active != "Y":
        return None
    
    return user


async def get_current_user(
    session: SessionDep,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> SecUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    token = credentials.credentials
    login = decode_access_token(token)
    
    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    result = await session.execute(select(SecUser).where(SecUser.login == login))
    user = result.scalars().first()
    
    if not user or user.active != "Y":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


async def get_user_group_ids(session: AsyncSession, login: str) -> list[int]:
    from app.models.security import SecUserGroupLink
    result = await session.execute(
        select(SecUserGroupLink.group_id).where(SecUserGroupLink.login == login)
    )
    return list(result.scalars().all())


async def is_user_admin(session: AsyncSession, user: SecUser) -> bool:
    """Verifica si el usuario es administrador por priv_admin o por grupo."""
    if user.priv_admin == "Y":
        return True
    group_ids = await get_user_group_ids(session, user.login)
    return ADMIN_GROUP_ID in group_ids


def require_permission(app_name: str | list[str], privilege: str = "priv_access"):
    async def permission_checker(
        session: SessionDep,
        current_user: SecUser = Depends(get_current_user),
    ):
        # Los administradores tienen todos los permisos
        if await is_user_admin(session, current_user):
            return current_user

        group_ids = await get_user_group_ids(session, current_user.login)

        if not group_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado para {app_name}:{privilege}",
            )

        app_names = [app_name] if isinstance(app_name, str) else app_name

        permission_result = await session.execute(
            select(SecGroupApp).where(
                SecGroupApp.group_id.in_(group_ids),
                SecGroupApp.app_name.in_(app_names),
                getattr(SecGroupApp, privilege) == "Y"
            )
        )

        has_permission = permission_result.first() is not None

        if not has_permission:
            detail_msg = f"Permisos insuficientes para {app_name}:{privilege}"
            if isinstance(app_name, list):
                detail_msg = f"Permisos insuficientes (requiere uno de {', '.join(app_name)}) para {privilege}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail_msg,
            )

        return current_user

    return permission_checker


CurrentUser = Annotated[SecUser, Depends(get_current_user)]
