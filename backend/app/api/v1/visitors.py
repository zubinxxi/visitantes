from fastapi import APIRouter, HTTPException, status, UploadFile, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import uuid

from app.api.deps import SessionDep, CurrentUser, CurrentUser
from app.models.visitor import Visitor
from app.schemas.visitor import VisitorCreate, VisitorRead, VisitorUpdate, PaginatedVisitorsResponse
from app.core.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

router = APIRouter(prefix="/visitors", tags=["visitors"])


@router.get("/", response_model=PaginatedVisitorsResponse)
async def get_all_visitors(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query("", max_length=100),
    session: SessionDep = None,
):
    offset = (page - 1) * limit
    
    query = select(Visitor)
    count_query = select(func.count()).select_from(Visitor)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Visitor.names.ilike(search_filter)) | 
            (Visitor.surnames.ilike(search_filter)) |
            (Visitor.id_card_number.ilike(search_filter))
        )
        count_query = count_query.where(
            (Visitor.names.ilike(search_filter)) | 
            (Visitor.surnames.ilike(search_filter)) |
            (Visitor.id_card_number.ilike(search_filter))
        )
    
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    items = result.scalars().all()
    
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/{visitor_id}", response_model=VisitorRead)
async def get_visitor(visitor_id: int, session: SessionDep):
    visitor = await session.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.get("/cedula/{cedula}", response_model=VisitorRead)
async def get_visitor_by_cedula(cedula: str, session: SessionDep):
    result = await session.execute(
        select(Visitor).where(Visitor.id_card_number == cedula)
    )
    visitor = result.scalars().first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.post("/", response_model=VisitorRead, status_code=status.HTTP_201_CREATED)
async def create_visitor(visitor_in: VisitorCreate, session: SessionDep):
    existing = await session.execute(
        select(Visitor).where(Visitor.id_card_number == visitor_in.id_card_number)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Visitor with this cedula already exists")

    visitor = Visitor(**visitor_in.model_dump())
    session.add(visitor)
    await session.commit()
    await session.refresh(visitor)
    return visitor


@router.put("/{visitor_id}", response_model=VisitorRead)
async def update_visitor(visitor_id: int, visitor_in: VisitorUpdate, session: SessionDep):
    visitor = await session.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    update_data = visitor_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(visitor, key, value)

    session.add(visitor)
    await session.commit()
    await session.refresh(visitor)
    return visitor


@router.delete("/{visitor_id}")
async def delete_visitor(visitor_id: int, session: SessionDep):
    visitor = await session.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    await session.delete(visitor)
    await session.commit()
    return {"message": "Visitor deleted successfully"}


@router.post("/{visitor_id}/upload-photo")
async def upload_photo(visitor_id: int, file: UploadFile, session: SessionDep):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo no permitido. Solo: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    visitor = await session.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    settings.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{visitor_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = settings.PHOTOS_DIR / filename

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    visitor.photo = f"/photos/visitors/{filename}"
    session.add(visitor)
    await session.commit()
    await session.refresh(visitor)

    return {
        "visitor_id": visitor.id,
        "filename": filename,
        "url": visitor.photo,
    }


@router.post("/upload-photo-temp")
async def upload_photo_temp(
    file: UploadFile,
    cedula: str = None,
    session: SessionDep = None,
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo no permitido. Solo: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    settings.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    # Use cedula for filename if provided
    if cedula:
        safe_cedula = cedula.replace("/", "-").replace("\\", "-")
        filename = f"{safe_cedula}.jpg"
    else:
        filename = f"temp_{uuid.uuid4().hex}.jpg"
    
    filepath = settings.PHOTOS_DIR / filename

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    url = f"/photos/visitors/{filename}"
    
    return {
        "filename": filename,
        "url": url,
    }
