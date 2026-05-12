from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class VisitBase(BaseModel):
    id_visitors: int
    id_type_of_proce: int
    company_represents: str
    purpose: str
    buildings_visited: str
    uadm_visited: str
    check_in: datetime
    check_out: Optional[datetime] = None
    user_created: Optional[str] = None


class VisitCreate(VisitBase):
    uadm_ids: list[int] = []
    building_ids: list[int] = []


class VisitRead(VisitBase):
    id: int
    uadms_names: Optional[str] = None
    buildings_names: Optional[str] = None
    names: Optional[str] = None
    surnames: Optional[str] = None
    id_card_number: Optional[str] = None
    photo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VisitListResponse(BaseModel):
    items: List[VisitRead]
    total: int
    total_pages: int
    page: int


class VisitUpdate(BaseModel):
    id_type_of_proce: Optional[int] = None
    company_represents: Optional[str] = None
    purpose: Optional[str] = None
    buildings_visited: Optional[str] = None
    uadm_visited: Optional[str] = None
    check_out: Optional[datetime] = None
    uadm_ids: Optional[list[int]] = None
    building_ids: Optional[list[int]] = None


class StatsSummary(BaseModel):
    total_visits: int
    active_visits: int
    today_visits: int
    unique_visitors: int


class CheckInRequest(BaseModel):
    id_card_number: str
    names: str
    surnames: str
    gender: str
    id_num_control: str = ""
    province: str = ""
    nationality: str = ""
    id_type_of_proce: int = 6
    company_represents: str = ""
    purpose: str = ""
    uadm_ids: list[int] = []
    building_ids: list[int] = []
    user_created: str = "sysadmin"
