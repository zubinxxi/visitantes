from pydantic import BaseModel, ConfigDict
from typing import Optional


class VisitorBase(BaseModel):
    names: str
    surnames: str
    gender: str
    id_card_number: str
    id_num_control: str
    province: str
    nationality: str
    photo: str
    user_created: Optional[str] = None


class VisitorCreate(VisitorBase):
    pass


class VisitorRead(VisitorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class VisitorUpdate(BaseModel):
    names: Optional[str] = None
    surnames: Optional[str] = None
    gender: Optional[str] = None
    id_card_number: Optional[str] = None
    id_num_control: Optional[str] = None
    province: Optional[str] = None
    nationality: Optional[str] = None
    photo: Optional[str] = None
    user_created: Optional[str] = None


class PaginatedVisitorsResponse(BaseModel):
    items: list[VisitorRead]
    total: int
    page: int
    limit: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
