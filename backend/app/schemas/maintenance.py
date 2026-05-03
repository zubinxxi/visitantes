from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProvinceBase(BaseModel):
    description: str


class ProvinceCreate(ProvinceBase):
    pass


class ProvinceRead(ProvinceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProvinceUpdate(BaseModel):
    description: Optional[str] = None


class InstitutionBase(BaseModel):
    description: Optional[str] = None
    code_mef: Optional[float] = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionRead(InstitutionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class InstitutionUpdate(BaseModel):
    description: Optional[str] = None
    code_mef: Optional[float] = None


class TypeUadmBase(BaseModel):
    description: Optional[str] = None


class TypeUadmCreate(TypeUadmBase):
    pass


class TypeUadmRead(TypeUadmBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TypeUadmUpdate(BaseModel):
    description: Optional[str] = None


class BuildingBase(BaseModel):
    code: str
    description: str


class BuildingCreate(BuildingBase):
    pass


class BuildingRead(BuildingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BuildingUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None


class TypeOfProcedureBase(BaseModel):
    description: str


class TypeOfProcedureCreate(TypeOfProcedureBase):
    pass


class TypeOfProcedureRead(TypeOfProcedureBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TypeOfProcedureUpdate(BaseModel):
    description: Optional[str] = None


class UadmBase(BaseModel):
    id_uadm_origin: Optional[int] = None
    name: Optional[str] = None
    initials: Optional[str] = None
    id_type_uadm: Optional[int] = None
    status: Optional[bool] = None
    dbo_C_DIR: Optional[int] = None
    dbo_C_DEPTO: Optional[int] = None
    dbo_C_SECCION: Optional[int] = None
    id_institution: Optional[int] = None
    id_province: Optional[int] = None
    id_district: Optional[int] = None
    id_district_subdivision: Optional[int] = None


class UadmCreate(UadmBase):
    pass


class UadmRead(UadmBase):
    id: int
    province_name: Optional[str] = None
    institution_name: Optional[str] = None
    type_uadm_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UadmUpdate(BaseModel):
    id_uadm_origin: Optional[int] = None
    name: Optional[str] = None
    initials: Optional[str] = None
    id_type_uadm: Optional[int] = None
    status: Optional[bool] = None
    dbo_C_DIR: Optional[int] = None
    dbo_C_DEPTO: Optional[int] = None
    dbo_C_SECCION: Optional[int] = None
    id_institution: Optional[int] = None
    id_province: Optional[int] = None
    id_district: Optional[int] = None
    id_district_subdivision: Optional[int] = None
