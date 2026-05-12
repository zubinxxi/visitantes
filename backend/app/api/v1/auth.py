from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUser
from app.core.security import (
    verify_password, 
    create_access_token, 
    hash_password,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.models.security import SecUser, SecUserGroupLink, SecGroupApp
from app.schemas.security import (
    SecGroupAppRead, 
    ChangePasswordRequest, 
    ForgotPasswordRequest, 
    ResetPasswordRequest,
)
from app.core.emails import send_reset_password_email

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


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, 
    session: SessionDep,
    background_tasks: BackgroundTasks,
):
    """
    Inicia el proceso de recuperación de contraseña enviando un correo.
    """
    print(f"DEBUG: Recuperar contraseña para: {payload.login_or_email}")
    # Buscar por login o email
    result = await session.execute(
        select(SecUser).where(
            (SecUser.login == payload.login_or_email) | 
            (SecUser.email == payload.login_or_email)
        )
    )
    user = result.scalars().first()

    if not user:
        print("DEBUG: Usuario no encontrado")
        # Por seguridad, no revelamos si el usuario existe o no
        return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}

    if not user.email:
         print(f"DEBUG: Usuario {user.login} no tiene email")
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene un correo electrónico configurado.",
        )

    print(f"DEBUG: Generando token para {user.login}")
    token = create_password_reset_token(user.login)
    
    print(f"DEBUG: Programando envío de correo a {user.email}")
    background_tasks.add_task(send_reset_password_email, user.email, user.login, token)

    return {"message": "Si el usuario existe, se ha enviado un correo de recuperación."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, session: SessionDep):
    """
    Restablece la contraseña usando un token válido.
    """
    login = verify_password_reset_token(payload.token)
    if not login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado",
        )

    result = await session.execute(select(SecUser).where(SecUser.login == login))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    user.pswd = hash_password(payload.new_password)
    session.add(user)
    await session.commit()

    return {"message": "Contraseña actualizada exitosamente"}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest, 
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Cambia la contraseña del usuario autenticado.
    """
    if not verify_password(payload.current_password, current_user.pswd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )

    current_user.pswd = hash_password(payload.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "Contraseña cambiada exitosamente"}
