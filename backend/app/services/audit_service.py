from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Optional


class ScLog(SQLModel, table=True):
    __tablename__ = "sc_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    inserted_date: Optional[datetime] = None
    username: str = Field(max_length=90)
    application: str = Field(max_length=255)
    creator: str = Field(max_length=30)
    ip_user: str = Field(max_length=255)
    action: str = Field(max_length=30)
    description: Optional[str] = None
