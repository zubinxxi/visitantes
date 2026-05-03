from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep
from app.services.qr_service import parse_cedula_qr
from app.models.visitor import Visitor
from app.schemas.visitor import VisitorRead

router = APIRouter(prefix="/qr", tags=["qr"])


class QrParseRequest(BaseModel):
    raw_data: str


class QrParseResponse(BaseModel):
    cedula: str
    provincia: str | None = None
    tomo: str | None = None
    numero: str | None = None
    format: str
    visitor_exists: bool = False
    visitor: VisitorRead | None = None


@router.post("/parse", response_model=QrParseResponse)
async def parse_qr(payload: QrParseRequest, session: SessionDep):
    parsed = parse_cedula_qr(payload.raw_data)
    response = QrParseResponse(
        cedula=parsed.get("cedula", payload.raw_data),
        provincia=parsed.get("provincia"),
        tomo=parsed.get("tomo"),
        numero=parsed.get("numero"),
        format=parsed.get("format", "raw"),
    )

    if response.format == "panama_cedula" or response.cedula:
        result = await session.execute(
            select(Visitor).where(Visitor.id_card_number == response.cedula)
        )
        visitor = result.scalars().first()
        if visitor:
            response.visitor_exists = True
            response.visitor = VisitorRead.model_validate(visitor)

    return response
