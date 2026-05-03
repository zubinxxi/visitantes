from typing import Generic, TypeVar, Type, Optional
from fastapi import HTTPException, Query
from sqlmodel import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    total_pages: int


class MaintenanceCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReadSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        read_schema: Type[ReadSchemaType],
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_schema = read_schema

    async def get_all(
        self,
        session: AsyncSession,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        search_fields: Optional[list[str]] = None,
    ) -> PaginatedResponse:
        offset = (page - 1) * limit
        
        from app.models.maintenance import Uadm as UadmModel, Province, Institution, TypeUadm
        
        search_conditions = []
        if search and search_fields:
            if self.model.__name__ == 'Uadm':
                search_conditions.append(UadmModel.name.ilike(f"%{search}%"))
                search_conditions.append(UadmModel.initials.ilike(f"%{search}%"))
                search_conditions.append(UadmModel.id_province.in_(
                    select(Province.id).where(Province.description.ilike(f"%{search}%"))
                ))
                search_conditions.append(UadmModel.id_institution.in_(
                    select(Institution.id).where(Institution.description.ilike(f"%{search}%"))
                ))
                search_conditions.append(UadmModel.id_type_uadm.in_(
                    select(TypeUadm.id).where(TypeUadm.description.ilike(f"%{search}%"))
                ))
                query = select(UadmModel).where(or_(*search_conditions))
                count_query = select(func.count()).select_from(UadmModel).where(or_(*search_conditions))
            else:
                for field in search_fields:
                    if hasattr(self.model, field):
                        search_conditions.append(getattr(self.model, field).ilike(f"%{search}%"))
                if search_conditions:
                    query = select(self.model).where(or_(*search_conditions))
                    count_query = select(func.count()).select_from(self.model).where(or_(*search_conditions))
                else:
                    query = select(self.model)
                    count_query = select(func.count()).select_from(self.model)
        else:
            query = select(self.model)
            count_query = select(func.count()).select_from(self.model)
        
        # Get total count
        result_count = await session.execute(count_query)
        total = result_count.scalar() or 0
        
        # Get paginated items
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        items = result.scalars().all()
        
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        
        from app.models.maintenance import Uadm, Province, Institution, TypeUadm
        
        read_items = []
        for i in items:
            item_dict = self.read_schema.model_validate(i).model_dump()
            if self.model.__name__ == 'Uadm':
                if i.id_province:
                    prov = await session.get(Province, i.id_province)
                    item_dict['province_name'] = prov.description if prov else ''
                else:
                    item_dict['province_name'] = ''
                if i.id_institution:
                    inst = await session.get(Institution, i.id_institution)
                    item_dict['institution_name'] = inst.description if inst else ''
                else:
                    item_dict['institution_name'] = ''
                if i.id_type_uadm:
                    t_uadm = await session.get(TypeUadm, i.id_type_uadm)
                    item_dict['type_uadm_name'] = t_uadm.description if t_uadm else ''
                else:
                    item_dict['type_uadm_name'] = ''
            read_items.append(item_dict)
        
        return PaginatedResponse(
            items=read_items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, session: AsyncSession, item_id: int) -> ReadSchemaType:
        item = await session.get(self.model, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return self.read_schema.model_validate(item)

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ReadSchemaType:
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return self.read_schema.model_validate(db_obj)

    async def update(
        self, session: AsyncSession, item_id: int, obj_in: UpdateSchemaType
    ) -> ReadSchemaType:
        item = await session.get(self.model, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return self.read_schema.model_validate(item)

    async def delete(self, session: AsyncSession, item_id: int) -> dict:
        item = await session.get(self.model, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        await session.delete(item)
        await session.commit()
        return {"message": "Deleted successfully"}
