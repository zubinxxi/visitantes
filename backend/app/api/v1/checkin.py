from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.api.deps import SessionDep, CurrentUser
from app.models.visit import Visit, VisitsUadmLink, VisitsBuildingsLink
from app.models.visitor import Visitor
from app.models.maintenance import Uadm, Building
from app.services.audit_service import ScLog
from app.schemas.visit import VisitRead
from app.core.utils import now_panama_naive


class QrProcessRequest(BaseModel):
    raw_data: str


class QrProcessResponse(BaseModel):
    needs_registration: bool
    visitor_data: Optional[dict] = None
    visitor: Optional[dict] = None
    visit: Optional[dict] = None


class RegisterRequest(BaseModel):
    raw_data: str
    photo: str = ""
    names: str = ""
    surnames: str = ""
    gender: str = "M"
    id_num_control: str = ""
    province: str = ""
    nationality: str = ""


class ConfirmCheckInRequest(BaseModel):
    visit_id: int
    uadm_ids: List[int] = []
    building_ids: List[int] = []
    company_represents: str = ""
    purpose: str = ""


class BadgeResponse(BaseModel):
    visit_id: int
    visitor_name: str
    id_card_number: str
    check_in: str
    uadms: str
    buildings: str
    qr_data: str


router = APIRouter(prefix="/checkin", tags=["checkin"])


def _build_log_entry(username: str, action: str, description: str) -> ScLog:
    return ScLog(
        inserted_date=now_panama_naive(),
        username=username,
        application="visitorsdb",
        creator=username,
        ip_user="127.0.0.1",
        action=action,
        description=description,
    )


def _parse_qr_data(raw_data: str) -> dict:
    parts = raw_data.split("|")
    if len(parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Formato QR inválido"
        )
    
    id_card_number = parts[0].strip() if parts[0] else ""
    names = parts[1].strip() if parts[1] else ""
    surnames = parts[2].strip() if len(parts) > 2 and parts[2] else ""
    gender = parts[4].strip().upper() if len(parts) > 4 and parts[4] else "M"
    
    province = ""
    if len(parts) > 5 and parts[5]:
        province = parts[5].strip().split(",")[0].strip()
    
    nationality = parts[7].strip() if len(parts) > 7 and parts[7] else ""
    
    id_num_control = parts[-1].strip() if parts[-1] else ""
    
    return {
        "id_card_number": id_card_number,
        "names": names,
        "surnames": surnames,
        "gender": gender,
        "province": province,
        "nationality": nationality,
        "id_num_control": id_num_control
    }


@router.post("/process-qr", response_model=QrProcessResponse)
async def process_qr(payload: QrProcessRequest, session: SessionDep, user: CurrentUser):
    parsed = _parse_qr_data(payload.raw_data)
    
    result = await session.execute(
        select(Visitor).where(Visitor.id_card_number == parsed["id_card_number"])
    )
    visitor = result.scalars().first()
    
    if not visitor:
        return QrProcessResponse(
            needs_registration=True,
            visitor_data=parsed
        )

    active_result = await session.execute(
        select(Visit).where(
            Visit.id_visitors == visitor.id,
            Visit.check_out.is_(None)
        )
    )
    existing_active = active_result.scalars().first()
    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El visitante tiene una visita activa"
        )

    visit = Visit(
        id_visitors=visitor.id,
        id_type_of_proce=6,
        company_represents="",
        purpose="",
        buildings_visited="",
        uadm_visited="",
        check_in=now_panama_naive(),
        user_created=user.login,
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)
    
    return QrProcessResponse(
        needs_registration=False,
        visitor={
            "id": visitor.id,
            "names": visitor.names,
            "surnames": visitor.surnames,
            "id_card_number": visitor.id_card_number,
            "photo": visitor.photo,
            "gender": visitor.gender,
            "province": visitor.province,
            "nationality": visitor.nationality
        },
        visit={
            "id": visit.id,
            "check_in": visit.check_in.isoformat() if visit.check_in else None
        }
    )


@router.post("/register", response_model=QrProcessResponse)
async def register_and_checkin(payload: RegisterRequest, session: SessionDep, user: CurrentUser):
    parsed = _parse_qr_data(payload.raw_data)
    
    id_card_number = parsed["id_card_number"]
    names = payload.names or parsed["names"]
    surnames = payload.surnames or parsed["surnames"]
    gender = payload.gender or parsed["gender"]
    id_num_control = payload.id_num_control or parsed["id_num_control"]
    province = payload.province or parsed["province"]
    nationality = payload.nationality or parsed["nationality"]
    
    result = await session.execute(
        select(Visitor).where(Visitor.id_card_number == id_card_number)
    )
    visitor = result.scalars().first()
    
    if visitor:
        raise HTTPException(status_code=409, detail="El visitante ya existe")
    
    visitor = Visitor(
        id_card_number=id_card_number,
        names=names,
        surnames=surnames,
        gender=gender,
        id_num_control=id_num_control,
        province=province,
        nationality=nationality,
        photo=payload.photo,
        user_created=user.login,
    )
    session.add(visitor)
    await session.flush()
    await session.refresh(visitor)
    
    visit = Visit(
        id_visitors=visitor.id,
        id_type_of_proce=6,
        company_represents="",
        purpose="",
        buildings_visited="",
        uadm_visited="",
        check_in=now_panama_naive(),
        user_created=user.login,
    )
    session.add(visit)
    
    session.add(
        _build_log_entry(
            username=user.login,
            action="CHECKIN",
            description=f"Check-in - {names} {surnames}",
        )
    )
    
    await session.commit()
    await session.refresh(visit)
    
    return QrProcessResponse(
        needs_registration=False,
        visitor={
            "id": visitor.id,
            "names": visitor.names,
            "surnames": visitor.surnames,
            "id_card_number": visitor.id_card_number,
            "photo": visitor.photo,
            "gender": visitor.gender,
            "province": visitor.province,
            "nationality": visitor.nationality
        },
        visit={
            "id": visit.id,
            "check_in": visit.check_in.isoformat() if visit.check_in else None
        }
    )


@router.post("/confirm", response_model=VisitRead)
async def confirm_checkin(payload: ConfirmCheckInRequest, session: SessionDep, user: CurrentUser):
    visit = await session.get(Visit, payload.visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    if payload.uadm_ids:
        uadms_str = ",".join(str(u) for u in payload.uadm_ids)
        visit.uadm_visited = uadms_str
        
        for uadm_id in payload.uadm_ids:
            session.add(VisitsUadmLink(id_visits=visit.id, id_uadm=uadm_id))
    
    if payload.building_ids:
        buildings_str = ",".join(str(b) for b in payload.building_ids)
        visit.buildings_visited = buildings_str
        
        for building_id in payload.building_ids:
            session.add(VisitsBuildingsLink(id_visits=visit.id, id_building=building_id))
    
    if payload.company_represents:
        visit.company_represents = payload.company_represents
    if payload.purpose:
        visit.purpose = payload.purpose
    
    session.add(
        _build_log_entry(
            username=user.login,
            action="CHECKIN",
            description=f"Check-in confirmado visita #{visit.id}",
        )
    )
    
    await session.commit()
    await session.refresh(visit)
    
    return visit


@router.get("/visits/{visit_id}/badge", response_model=BadgeResponse)
async def get_visit_badge(visit_id: int, session: SessionDep):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    visitor = await session.get(Visitor, visit.id_visitors)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado")
    
    uadms_names = ""
    uadm_ids_str = visit.uadm_visited
    if uadm_ids_str:
        uadm_ids_list = [int(x) for x in uadm_ids_str.replace(";", ",").split(",") if x and x.isdigit()]
        if uadm_ids_list:
            result = await session.execute(
                select(Uadm.name).where(Uadm.id.in_(uadm_ids_list))
            )
            uadms_names = ", ".join(result.scalars().all() or [])
    
    buildings_names = ""
    building_ids_str = visit.buildings_visited
    if building_ids_str:
        building_ids_list = [int(x) for x in building_ids_str.replace(";", ",").split(",") if x and x.isdigit()]
        if building_ids_list:
            result = await session.execute(
                select(Building.description).where(Building.id.in_(building_ids_list))
            )
            buildings_names = ", ".join(result.scalars().all() or [])
    
    return BadgeResponse(
        visit_id=visit.id,
        visitor_name=f"{visitor.names} {visitor.surnames}",
        id_card_number=visitor.id_card_number,
        check_in=visit.check_in.isoformat() if visit.check_in else "",
        uadms=uadms_names,
        buildings=visit.buildings_visited or "",
        qr_data=str(visit.id)
    )