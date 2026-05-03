from typing import Annotated
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_session
from app.core.security import decode_access_token
from app.models.security import SecUser

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


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
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> SecUser:
    token = credentials.credentials
    logger.warning(f"DEBUG: Received token: {token[:50]}...")
    
    login = decode_access_token(token)
    logger.warning(f"DEBUG: Decoded login: {login}")
    
    if not login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await session.execute(select(SecUser).where(SecUser.login == login))
    user = result.scalars().first()
    
    logger.warning(f"DEBUG: User from DB: {user}")

    if not user or user.active != "Y":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


CurrentUser = Annotated[SecUser, Depends(get_current_user)]
