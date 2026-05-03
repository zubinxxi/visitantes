from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

from app.api.deps import SessionDep, CurrentUser
from app.models.security import SecUser
from app.models.visit import Visit, VisitsUadmLink, VisitsBuildingsLink
from app.models.visitor import Visitor
from app.models.maintenance import Uadm, Building
from app.services.audit_service import ScLog
from app.schemas.visit import VisitRead, VisitUpdate, CheckInRequest, VisitListResponse

router = APIRouter(prefix="/visits", tags=["visits"])


async def _get_uadm_names(session: AsyncSession, uadm_ids_str: str) -> str:
    if not uadm_ids_str:
        return ""
    uadm_ids_list = [int(x) for x in uadm_ids_str.replace(";", ",").split(",") if x and x.isdigit()]
    if not uadm_ids_list:
        return ""
    result = await session.execute(
        select(Uadm.name).where(Uadm.id.in_(uadm_ids_list))
    )
    return ", ".join(result.scalars().all() or [])


async def _get_building_names(session: AsyncSession, building_ids_str: str) -> str:
    if not building_ids_str:
        return ""
    building_ids_list = [int(x) for x in building_ids_str.replace(";", ",").split(",") if x and x.isdigit()]
    if not building_ids_list:
        return ""
    result = await session.execute(
        select(Building.description).where(Building.id.in_(building_ids_list))
    )
    return ", ".join(result.scalars().all() or [])


def _build_log_entry(username: str, action: str, description: str) -> ScLog:
    return ScLog(
        inserted_date=datetime.now(timezone.utc),
        username=username,
        application="visitorsdb",
        creator=username,
        ip_user="127.0.0.1",
        action=action,
        description=description,
    )


@router.get("/", response_model=list[VisitRead])
async def get_all_visits(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    result = await session.execute(
        select(Visit).order_by(Visit.check_in.desc()).offset(offset).limit(limit)
    )
    visits = result.scalars().all()
    
    visit_list = []
    for visit in visits:
        visitor = await session.get(Visitor, visit.id_visitors)
        
        visit_dict = VisitRead(
            id=visit.id,
            id_visitors=visit.id_visitors,
            id_type_of_proce=visit.id_type_of_proce,
            company_represents=visit.company_represents,
            purpose=visit.purpose,
            buildings_visited=visit.buildings_visited,
            uadm_visited=visit.uadm_visited,
            check_in=visit.check_in,
            check_out=visit.check_out,
            user_created=visit.user_created,
        )
        if visitor:
            visit_dict.names = visitor.names
            visit_dict.surnames = visitor.surnames
            visit_dict.id_card_number = visitor.id_card_number
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)
    
    return visit_list


@router.get("/paginated", response_model=VisitListResponse)
async def get_visits_paginated(
    session: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str = Query(default=""),
    active_filter: str = Query(default=""),
):
    offset = (page - 1) * limit
    
    query = select(Visit).order_by(Visit.check_in.desc())
    
    if active_filter == "true":
        query = query.where(Visit.check_out.is_(None))
    elif active_filter == "false":
        query = query.where(Visit.check_out.isnot(None))
    
    count_query = select(func.count(Visit.id))
    if active_filter == "true":
        count_query = count_query.where(Visit.check_out.is_(None))
    elif active_filter == "false":
        count_query = count_query.where(Visit.check_out.isnot(None))
    
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0
    
    result = await session.execute(query.offset(offset).limit(limit))
    visits = result.scalars().all()
    
    visit_list = []
    for visit in visits:
        visitor = await session.get(Visitor, visit.id_visitors)
        
        visit_dict = VisitRead(
            id=visit.id,
            id_visitors=visit.id_visitors,
            id_type_of_proce=visit.id_type_of_proce,
            company_represents=visit.company_represents,
            purpose=visit.purpose,
            buildings_visited=visit.buildings_visited,
            uadm_visited=visit.uadm_visited,
            check_in=visit.check_in,
            check_out=visit.check_out,
            user_created=visit.user_created,
        )
        if visitor:
            visit_dict.names = visitor.names
            visit_dict.surnames = visitor.surnames
            visit_dict.id_card_number = visitor.id_card_number
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)
    
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return VisitListResponse(
        items=visit_list,
        total=total,
        total_pages=total_pages,
        page=page
    )


@router.get("/active", response_model=list[VisitRead])
async def get_active_visits(session: SessionDep):
    result = await session.execute(
        select(Visit)
        .where(Visit.check_out.is_(None))
        .order_by(Visit.check_in.desc())
    )
    visits = result.scalars().all()
    
    visit_list = []
    for visit in visits:
        visitor = await session.get(Visitor, visit.id_visitors)
        
        visit_dict = VisitRead(
            id=visit.id,
            id_visitors=visit.id_visitors,
            id_type_of_proce=visit.id_type_of_proce,
            company_represents=visit.company_represents,
            purpose=visit.purpose,
            buildings_visited=visit.buildings_visited,
            uadm_visited=visit.uadm_visited,
            check_in=visit.check_in,
            check_out=visit.check_out,
            user_created=visit.user_created,
        )
        if visitor:
            visit_dict.names = visitor.names
            visit_dict.surnames = visitor.surnames
            visit_dict.id_card_number = visitor.id_card_number
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)
    
    return visit_list


@router.get("/today", response_model=list[VisitRead])
async def get_today_visits(session: SessionDep):
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    result = await session.execute(
        select(Visit)
        .where(Visit.check_in >= today_start)
        .order_by(Visit.check_in.desc())
    )
    visits = result.scalars().all()
    
    visit_list = []
    for visit in visits:
        visitor = await session.get(Visitor, visit.id_visitors)
        
        visit_dict = VisitRead(
            id=visit.id,
            id_visitors=visit.id_visitors,
            id_type_of_proce=visit.id_type_of_proce,
            company_represents=visit.company_represents,
            purpose=visit.purpose,
            buildings_visited=visit.buildings_visited,
            uadm_visited=visit.uadm_visited,
            check_in=visit.check_in,
            check_out=visit.check_out,
            user_created=visit.user_created,
        )
        if visitor:
            visit_dict.names = visitor.names
            visit_dict.surnames = visitor.surnames
            visit_dict.id_card_number = visitor.id_card_number
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)
    
    return visit_list


@router.get("/{visit_id}", response_model=VisitRead)
async def get_visit(visit_id: int, session: SessionDep):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.get("/stats/summary")
async def get_stats(session: SessionDep):
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    total_result = await session.execute(select(func.count(Visit.id)))
    total_visits = total_result.scalar() or 0

    active_result = await session.execute(
        select(func.count(Visit.id)).where(Visit.check_out.is_(None))
    )
    active_visits = active_result.scalar() or 0

    today_result = await session.execute(
        select(func.count(Visit.id)).where(Visit.check_in >= today_start)
    )
    today_visits = today_result.scalar() or 0

    unique_result = await session.execute(
        select(func.count(func.distinct(Visitor.id_card_number)))
        .select_from(Visit)
        .outerjoin(Visitor, Visit.id_visitors == Visitor.id)
    )
    unique_visitors = unique_result.scalar() or 0

    return {
        "total_visits": total_visits,
        "active_visits": active_visits,
        "today_visits": today_visits,
        "unique_visitors": unique_visitors,
    }


@router.post("/checkin", response_model=VisitRead, status_code=status.HTTP_201_CREATED)
async def check_in(payload: CheckInRequest, session: SessionDep):
    user_login = getattr(payload, 'user_created', None) or "sysadmin"

    visitor_result = await session.execute(
        select(Visitor).where(Visitor.id_card_number == payload.id_card_number)
    )
    visitor = visitor_result.scalars().first()

    if not visitor:
        visitor = Visitor(
            names=payload.names,
            surnames=payload.surnames,
            gender=payload.gender,
            id_card_number=payload.id_card_number,
            id_num_control=payload.id_num_control,
            province=payload.province,
            nationality=payload.nationality,
            photo="",
            user_created=user_login,
        )
        session.add(visitor)
        await session.flush()

    buildings_str = ",".join(str(b) for b in payload.building_ids)
    uadms_str = ",".join(str(u) for u in payload.uadm_ids)

    visit = Visit(
        id_visitors=visitor.id,
        id_type_of_proce=payload.id_type_of_proce,
        company_represents=payload.company_represents,
        purpose=payload.purpose,
        buildings_visited=buildings_str,
        uadm_visited=uadms_str,
        check_in=datetime.now(timezone.utc),
        user_created=user_login,
    )
    session.add(visit)
    await session.flush()

    for uadm_id in payload.uadm_ids:
        session.add(VisitsUadmLink(id_visits=visit.id, id_uadm=uadm_id))

    for building_id in payload.building_ids:
        session.add(VisitsBuildingsLink(id_visits=visit.id, id_building=building_id))

    session.add(
        _build_log_entry(
            username=user_login,
            action="CHECKIN",
            description=f"Check-in visita #{visit.id} - {visitor.names} {visitor.surnames} ({visitor.id_card_number})",
        )
    )

    await session.commit()
    await session.refresh(visit)

    return visit


@router.post("/{visit_id}/checkout", response_model=VisitRead)
async def check_out(visit_id: int, session: SessionDep, user: CurrentUser):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit.check_out is not None:
        raise HTTPException(status_code=400, detail="Visit already checked out")

    visitor_result = await session.execute(
        select(Visitor).where(Visitor.id == visit.id_visitors)
    )
    visitor = visitor_result.scalars().first()

    visit.check_out = datetime.now(timezone.utc)
    session.add(visit)
    
    username = user.login if user else "sysadmin"
    session.add(
        _build_log_entry(
            username=username,
            action="CHECKOUT",
            description=f"Check-out visita #{visit.id} - {visitor.names} {visitor.surnames}" if visitor else f"Check-out visita #{visit_id}",
        )
    )
    await session.commit()
    await session.refresh(visit)

    return visit


@router.put("/{visit_id}", response_model=VisitRead)
async def update_visit(visit_id: int, visit_in: VisitUpdate, session: SessionDep):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    update_data = visit_in.model_dump(exclude_unset=True)
    uadm_ids = update_data.pop("uadm_ids", None)
    building_ids = update_data.pop("building_ids", None)

    for key, value in update_data.items():
        setattr(visit, key, value)

    if uadm_ids is not None:
        result = await session.execute(
            select(VisitsUadmLink).where(VisitsUadmLink.id_visits == visit_id)
        )
        for link in result.scalars().all():
            await session.delete(link)
        for uadm_id in uadm_ids:
            session.add(VisitsUadmLink(id_visits=visit_id, id_uadm=uadm_id))

    if building_ids is not None:
        result = await session.execute(
            select(VisitsBuildingsLink).where(VisitsBuildingsLink.id_visits == visit_id)
        )
        for link in result.scalars().all():
            await session.delete(link)
        for building_id in building_ids:
            session.add(VisitsBuildingsLink(id_visits=visit_id, id_building=building_id))

    session.add(visit)
    await session.commit()
    await session.refresh(visit)
    return visit


@router.delete("/{visit_id}")
async def delete_visit(visit_id: int, session: SessionDep):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    result = await session.execute(
        select(VisitsUadmLink).where(VisitsUadmLink.id_visits == visit_id)
    )
    for link in result.scalars().all():
        await session.delete(link)

    result = await session.execute(
        select(VisitsBuildingsLink).where(VisitsBuildingsLink.id_visits == visit_id)
    )
    for link in result.scalars().all():
        await session.delete(link)

    await session.delete(visit)
    await session.commit()
    return {"message": "Visit deleted successfully"}
