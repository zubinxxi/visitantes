from sqlmodel import SQLModel, Field
from typing import Optional


class Province(SQLModel, table=True):
    __tablename__ = "province"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=45)


class Institution(SQLModel, table=True):
    __tablename__ = "institutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, max_length=100)
    code_mef: Optional[float] = None


class TypeUadm(SQLModel, table=True):
    __tablename__ = "type_uadm"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, max_length=45)


class Building(SQLModel, table=True):
    __tablename__ = "building"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=10)
    description: str = Field(max_length=200)


class TypeOfProcedure(SQLModel, table=True):
    __tablename__ = "type_of_procedure"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=200)


class Uadm(SQLModel, table=True):
    __tablename__ = "uadm"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_uadm_origin: Optional[int] = Field(default=None, foreign_key="uadm.id")
    name: Optional[str] = Field(default=None, max_length=100)
    initials: Optional[str] = Field(default=None, max_length=10)
    id_type_uadm: Optional[int] = Field(default=None, foreign_key="type_uadm.id")
    status: Optional[bool] = None
    dbo_C_DIR: Optional[int] = None
    dbo_C_DEPTO: Optional[int] = None
    dbo_C_SECCION: Optional[int] = None
    id_institution: Optional[int] = Field(default=None, foreign_key="institutions.id")
    id_province: Optional[int] = Field(default=None, foreign_key="province.id")
    id_district: Optional[int] = None
    id_district_subdivision: Optional[int] = None
