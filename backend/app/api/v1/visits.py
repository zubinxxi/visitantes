import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.deps import SessionDep, CurrentUser, require_permission
from app.models.visit import Visit, VisitsUadmLink, VisitsBuildingsLink
from app.core.utils import now_panama_naive, today_start_panama
from app.models.visitor import Visitor
from app.models.maintenance import Uadm, Building
from app.services.audit_service import ScLog
from app.schemas.visit import VisitRead, VisitUpdate, VisitListResponse, StatsSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visits", tags=["visits"])


async def _audit(session: AsyncSession, username: str, action: str, description: str):
    log_entry = ScLog(
        inserted_date=now_panama_naive(),
        username=username,
        application="visitorsdb",
        creator=username,
        ip_user="127.0.0.1",
        action=action,
        description=description
    )
    session.add(log_entry)
    await session.flush()


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
        inserted_date=now_panama_naive(),
        username=username,
        application="visitorsdb",
        creator=username,
        ip_user="127.0.0.1",
        action=action,
        description=description,
    )


@router.get("/", response_model=list[VisitRead], dependencies=[Depends(require_permission("visitors", "priv_access"))])
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
            visit_dict.photo = visitor.photo
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)
    
    return visit_list


@router.get("/paginated", response_model=VisitListResponse, dependencies=[Depends(require_permission("visitors", "priv_access"))])
async def get_visits_paginated(
    session: SessionDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str = Query(default=""),
    active_filter: str = Query(default=""),
    date: str = Query(default="", description="Filter by date (YYYY-MM-DD)"),
    start_date: str = Query(default="", description="Filter by start date (YYYY-MM-DD)"),
    end_date: str = Query(default="", description="Filter by end date (YYYY-MM-DD)"),
):
    offset = (page - 1) * limit

    base_query = select(Visit, Visitor).join(Visitor, Visit.id_visitors == Visitor.id)
    base_count = select(func.count(Visit.id)).join(Visitor, Visit.id_visitors == Visitor.id)

    if active_filter == "true":
        base_query = base_query.where(Visit.check_out.is_(None))
        base_count = base_count.where(Visit.check_out.is_(None))
    elif active_filter == "false":
        base_query = base_query.where(Visit.check_out.isnot(None))
        base_count = base_count.where(Visit.check_out.isnot(None))

    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) == date_obj)
            base_count = base_count.where(func.date(Visit.check_in) == date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de fecha inválido: '{date}'. Use YYYY-MM-DD.",
            )
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) >= start_date_obj)
            base_count = base_count.where(func.date(Visit.check_in) >= start_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de fecha inicial inválido: '{start_date}'. Use YYYY-MM-DD.",
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) <= end_date_obj)
            base_count = base_count.where(func.date(Visit.check_in) <= end_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Formato de fecha final inválido: '{end_date}'. Use YYYY-MM-DD.",
            )

    if search:
        search_filter = (
            Visitor.names.like(f"%{search}%")
            | Visitor.surnames.like(f"%{search}%")
            | Visitor.id_card_number.like(f"%{search}%")
        )
        base_query = base_query.where(search_filter)
        base_count = base_count.where(search_filter)

    base_query = base_query.order_by(Visit.check_in.desc())

    total_result = await session.execute(base_count)
    total = total_result.scalar() or 0

    result = await session.execute(base_query.offset(offset).limit(limit))
    rows = result.all()

    visit_list = []
    for visit, visitor in rows:
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
            names=visitor.names,
            surnames=visitor.surnames,
            id_card_number=visitor.id_card_number,
            photo=visitor.photo,
        )
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


@router.get("/export", response_model=list[VisitRead], dependencies=[Depends(require_permission("visitors", "priv_access"))])
async def get_visits_export(
    session: SessionDep,
    search: str = Query(default=""),
    active_filter: str = Query(default=""),
    date: str = Query(default="", description="Filter by date (YYYY-MM-DD)"),
    start_date: str = Query(default="", description="Filter by start date (YYYY-MM-DD)"),
    end_date: str = Query(default="", description="Filter by end date (YYYY-MM-DD)"),
):
    base_query = select(Visit, Visitor).join(Visitor, Visit.id_visitors == Visitor.id)

    if active_filter == "true":
        base_query = base_query.where(Visit.check_out.is_(None))
    elif active_filter == "false":
        base_query = base_query.where(Visit.check_out.isnot(None))

    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) == date_obj)
        except ValueError:
            pass 
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) >= start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            base_query = base_query.where(func.date(Visit.check_in) <= end_date_obj)
        except ValueError:
            pass

    if search:
        search_filter = (
            Visitor.names.like(f"%{search}%")
            | Visitor.surnames.like(f"%{search}%")
            | Visitor.id_card_number.like(f"%{search}%")
        )
        base_query = base_query.where(search_filter)

    base_query = base_query.order_by(Visit.check_in.desc())
    
    result = await session.execute(base_query)
    rows = result.all()

    visit_list = []
    for visit, visitor in rows:
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
            names=visitor.names,
            surnames=visitor.surnames,
            id_card_number=visitor.id_card_number,
            photo=visitor.photo,
        )
        visit_dict.uadms_names = await _get_uadm_names(session, visit.uadm_visited)
        visit_dict.buildings_names = await _get_building_names(session, visit.buildings_visited)
        visit_list.append(visit_dict)

    return visit_list


@router.get("/active", response_model=list[VisitRead], dependencies=[Depends(require_permission("visitors", "priv_access"))])
async def get_active_visits(
    session: SessionDep,
):
    result = await session.execute(
        select(Visit, Visitor)
        .join(Visitor, Visit.id_visitors == Visitor.id)
        .where(Visit.check_out.is_(None))
        .order_by(Visit.check_in.desc())
    )
    visits = result.all()
    
    visit_list = []
    for visit, visitor in visits:
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
        visit_list.append(visit_dict)
    
    return visit_list


@router.post("/checkout-by-qr", dependencies=[Depends(require_permission("visitors", "priv_delete"))])
async def checkout_by_qr(
    request: dict,
    session: SessionDep,
    current_user: CurrentUser,
):
    visit_id = request.get("visit_id")
    if not visit_id:
        raise HTTPException(status_code=400, detail="visit_id es requerido")
    
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    if visit.check_out:
        raise HTTPException(status_code=400, detail="La visita ya tiene check-out registrado")
    
    visitor = await session.get(Visitor, visit.id_visitors)
    
    visit.check_out = now_panama_naive()

    await _audit(
        session,
        username=current_user.login,
        action="CHECKOUT",
        description=f"Checkout by QR - {visitor.names} {visitor.surnames}",
    )
    await session.commit()
    await session.refresh(visit)

    return {
        "visit_id": visit.id,
        "visitor_names": visitor.names,
        "visitor_surnames": visitor.surnames,
        "check_out": visit.check_out.isoformat(),
    }


@router.post("/{visit_id}/checkout", dependencies=[Depends(require_permission("visitors", "priv_delete"))])
async def checkout_by_id(
    visit_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    visit = await session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    if visit.check_out:
        raise HTTPException(status_code=400, detail="La visita ya tiene check-out registrado")
    
    visitor = await session.get(Visitor, visit.id_visitors)
    
    visit.check_out = now_panama_naive()

    await _audit(
        session,
        username=current_user.login,
        action="CHECKOUT",
        description=f"Checkout visita #{visit.id} - {visitor.names} {visitor.surnames}",
    )
    await session.commit()
    await session.refresh(visit)

    return VisitRead(
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


@router.get("/stats/summary", response_model=StatsSummary, dependencies=[Depends(require_permission("visitors", "priv_access"))])
async def get_stats_summary(session: SessionDep) -> StatsSummary:
    try:
        total_result = await session.execute(select(func.count(Visit.id)))
        total_visits = total_result.scalar() or 0

        active_result = await session.execute(
            select(func.count(Visit.id)).where(Visit.check_out.is_(None))
        )
        active_visits = active_result.scalar() or 0

        today_start = today_start_panama().replace(tzinfo=None)
        today_result = await session.execute(
            select(func.count(Visit.id)).where(Visit.check_in >= today_start)
        )
        today_visits = today_result.scalar() or 0

        unique_result = await session.execute(
            select(func.count(Visitor.id))
        )
        unique_visitors = unique_result.scalar() or 0

        return StatsSummary(
            total_visits=total_visits,
            active_visits=active_visits,
            today_visits=today_visits,
            unique_visitors=unique_visitors,
        )
    except Exception:
        logger.exception("Error al obtener estadísticas del dashboard")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas del dashboard",
        )


@router.post("/checkin", response_model=VisitRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("visitors", "priv_insert"))])
async def create_checkin(
    request: dict,
    session: SessionDep,
    current_user: CurrentUser,
):
    id_card_number = request.get("id_card_number")
    names = request.get("names")
    surnames = request.get("surnames")
    gender = request.get("gender", "M")
    id_num_control = request.get("id_num_control", "")
    province = request.get("province", "")
    nationality = request.get("nationality", "")
    company_represents = request.get("company_represents", "")
    purpose = request.get("purpose", "")
    uadm_ids = request.get("uadm_ids", [])
    building_ids = request.get("building_ids", [])
    id_type_of_proce = request.get("id_type_of_proce", 6)
    user_created = request.get("user_created", current_user.login)
    
    visitor_result = await session.execute(
        select(Visitor).where(Visitor.id_card_number == id_card_number)
    )
    visitor = visitor_result.scalars().first()
    
    if not visitor:
        visitor = Visitor(
            id_card_number=id_card_number,
            names=names,
            surnames=surnames,
            gender=gender,
            id_num_control=id_num_control,
            province=province,
            nationality=nationality,
            photo="",  # Default empty string for photo
            user_created=user_created,
        )
        session.add(visitor)
        await session.flush()
        await session.refresh(visitor)
    else:
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
                detail=f"El visitante {visitor.names} {visitor.surnames} ya tiene una visita activa"
            )
    
    visit = Visit(
        id_visitors=visitor.id,
        id_type_of_proce=id_type_of_proce,
        company_represents=company_represents,
        purpose=purpose,
        buildings_visited="",
        uadm_visited="",
        check_in=now_panama_naive(),
        user_created=user_created,
    )
    session.add(visit)
    
    if uadm_ids:
        for uadm_id in uadm_ids:
            link = VisitsUadmLink(id_visits=None, id_uadm=uadm_id)
            link.id_visits = visit.id
            session.add(link)
    
    if building_ids:
        for building_id in building_ids:
            link = VisitsBuildingsLink(id_visits=None, id_building=building_id)
            link.id_visits = visit.id
            session.add(link)
    
    await _audit(
        session,
        username=user_created,
        action="CHECKIN",
        description=f"Check-in - {names} {surnames}",
    )
    await session.commit()
    await session.refresh(visit)
    
    return VisitRead(
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
        names=visitor.names,
        surnames=visitor.surnames,
        id_card_number=visitor.id_card_number,
    )
