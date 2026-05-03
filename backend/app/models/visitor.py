from sqlmodel import SQLModel, Field
from typing import Optional


class Visitor(SQLModel, table=True):
    __tablename__ = "visitors"

    id: Optional[int] = Field(default=None, primary_key=True)
    names: str = Field(max_length=60)
    surnames: str = Field(max_length=60)
    gender: str = Field(max_length=1)
    id_card_number: str = Field(max_length=60, unique=True)
    id_num_control: str = Field(max_length=60)
    province: str = Field(max_length=60)
    nationality: str = Field(max_length=60)
    photo: str = Field(max_length=100)
    user_created: str = Field(max_length=255)
