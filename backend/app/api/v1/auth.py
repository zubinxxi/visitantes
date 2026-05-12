from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.security import verify_password, create_access_token
from app.models.security import SecUser, SecUserGroupLink, SecGroupApp
from app.schemas.security import SecGroupAppRead

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
async def login(payload: LoginRequest, session: SessionDep):
    result = await session.execute(
        select(SecUser).where(SecUser.login == payload.login)
    )
    user = result.scalars().first()

    if not user or not verify_password(payload.password, user.pswd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if user.active != "Y":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token = create_access_token(subject=user.login, name=user.name or "", role=user.role or "")

    # Obtener IDs de los grupos del usuario
    user_groups_result = await session.execute(
        select(SecUserGroupLink.group_id).where(SecUserGroupLink.login == user.login)
    )
    group_ids = list(user_groups_result.scalars().all())

    # Obtener permisos de todos los grupos del usuario
    permissions_result = await session.execute(
        select(SecGroupApp).where(SecGroupApp.group_id.in_(group_ids))
    )
    permissions = permissions_result.scalars().all()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "priv_admin": user.priv_admin,
            "role": user.role,
        },
        "group_ids": group_ids,
        "permissions": [SecGroupAppRead.model_validate(p).model_dump() for p in permissions],
    }
