from pydantic import BaseModel, ConfigDict, field_validator
import re
from typing import Optional
from datetime import datetime


class SecGroupBase(BaseModel):
    description: Optional[str] = None


class SecGroupCreate(SecGroupBase):
    pass


class SecGroupRead(SecGroupBase):
    group_id: int

    model_config = ConfigDict(from_attributes=True)


class SecGroupUpdate(BaseModel):
    description: Optional[str] = None


class SecAppBase(BaseModel):
    app_name: str
    app_type: Optional[str] = None
    description: Optional[str] = None


class SecAppCreate(SecAppBase):
    pass


class SecAppRead(SecAppBase):
    model_config = ConfigDict(from_attributes=True)


class SecAppUpdate(BaseModel):
    app_type: Optional[str] = None
    description: Optional[str] = None


class SecGroupAppBase(BaseModel):
    group_id: int
    app_name: str
    priv_access: Optional[str] = None
    priv_insert: Optional[str] = None
    priv_delete: Optional[str] = None
    priv_update: Optional[str] = None
    priv_export: Optional[str] = None
    priv_print: Optional[str] = None


class SecGroupAppCreate(SecGroupAppBase):
    pass


class SecGroupAppRead(SecGroupAppBase):
    model_config = ConfigDict(from_attributes=True)


class SecGroupAppUpdate(BaseModel):
    priv_access: Optional[str] = None
    priv_insert: Optional[str] = None
    priv_delete: Optional[str] = None
    priv_update: Optional[str] = None
    priv_export: Optional[str] = None
    priv_print: Optional[str] = None


class SecUserBase(BaseModel):
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = None
    priv_admin: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None


class SecUserCreate(SecUserBase):
    pswd: str

    @field_validator("pswd")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class SecUserRead(SecUserBase):
    pswd_last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SecUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = None
    priv_admin: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    pswd: Optional[str] = None

    @field_validator("pswd")
    @classmethod
    def validate_password_complexity(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class ForgotPasswordRequest(BaseModel):
    login_or_email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v
