from fastapi import APIRouter, Depends, Response, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.models.category import CategoryCreate, CategoryRead, CategoryUpdate

from app.service import categories as service

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/{category_id}", response_model=CategoryRead)
async def read(category_id: int, db: AsyncSession = Depends(get_session)) -> CategoryRead:
    return await service.get(db, category_id)

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_session)) -> CategoryRead:
    return await service.create(db, data)

@router.put("/{category_id}", response_model=CategoryRead)
async def update(category_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_session)) -> CategoryRead:
    return await service.update(db, category_id, data)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(category_id: int, db: AsyncSession = Depends(get_session)) -> Response:
    await service.delete(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)