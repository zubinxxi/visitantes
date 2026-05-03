from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class SecGroup(SQLModel, table=True):
    __tablename__ = "sec_groups"

    group_id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, max_length=255)


class SecApp(SQLModel, table=True):
    __tablename__ = "sec_apps"

    app_name: str = Field(primary_key=True, max_length=128)
    app_type: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class SecUser(SQLModel, table=True):
    __tablename__ = "sec_users"

    login: str = Field(primary_key=True, max_length=255)
    pswd: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    active: Optional[str] = Field(default=None, max_length=1)
    activation_code: Optional[str] = Field(default=None, max_length=32)
    priv_admin: Optional[str] = Field(default=None, max_length=1)
    mfa: Optional[str] = Field(default=None, max_length=255)
    picture: Optional[bytes] = None
    role: Optional[str] = Field(default=None, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=64)
    pswd_last_updated: Optional[datetime] = None
    mfa_last_updated: Optional[datetime] = None


class SecUserGroupLink(SQLModel, table=True):
    __tablename__ = "sec_users_groups"

    login: str = Field(primary_key=True, foreign_key="sec_users.login")
    group_id: int = Field(primary_key=True, foreign_key="sec_groups.group_id")


class SecGroupApp(SQLModel, table=True):
    __tablename__ = "sec_groups_apps"

    group_id: int = Field(
        primary_key=True, foreign_key="sec_groups.group_id"
    )
    app_name: str = Field(
        primary_key=True, foreign_key="sec_apps.app_name"
    )
    priv_access: Optional[str] = Field(default=None, max_length=1)
    priv_insert: Optional[str] = Field(default=None, max_length=1)
    priv_delete: Optional[str] = Field(default=None, max_length=1)
    priv_update: Optional[str] = Field(default=None, max_length=1)
    priv_export: Optional[str] = Field(default=None, max_length=1)
    priv_print: Optional[str] = Field(default=None, max_length=1)
