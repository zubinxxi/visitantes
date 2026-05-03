from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class VisitsUadmLink(SQLModel, table=True):
    __tablename__ = "visits_uadm"

    id_visits: int = Field(primary_key=True, foreign_key="visits.id")
    id_uadm: int = Field(primary_key=True, foreign_key="uadm.id")


class VisitsBuildingsLink(SQLModel, table=True):
    __tablename__ = "visits_buildings"

    id_visits: int = Field(primary_key=True, foreign_key="visits.id")
    id_building: int = Field(primary_key=True, foreign_key="building.id")


class Visit(SQLModel, table=True):
    __tablename__ = "visits"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_visitors: int = Field(foreign_key="visitors.id")
    id_type_of_proce: int = Field(foreign_key="type_of_procedure.id")
    company_represents: str = Field(max_length=200)
    purpose: str = Field(max_length=200)
    buildings_visited: str = Field(max_length=60)
    uadm_visited: str = Field(max_length=60)
    check_in: datetime = Field()
    check_out: Optional[datetime] = None
    user_created: Optional[str] = Field(default=None, max_length=255)
