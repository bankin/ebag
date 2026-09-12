from fastapi import APIRouter, Depends, Response, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.models.product import ProductCreate, ProductRead, ProductUpdate

from app.service import products as service

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/{product_id:int}", response_model=ProductRead)
async def read(product_id: int, db: AsyncSession = Depends(get_session)) -> ProductRead:
    return await service.get(db, product_id)

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create(data: ProductCreate, db: AsyncSession = Depends(get_session)) -> ProductRead:
    return await service.create(db, data)

@router.put("/{product_id:int}", response_model=ProductRead)
async def update(product_id: int, data: ProductUpdate, db: AsyncSession = Depends(get_session)) -> ProductRead:
    return await service.update(db, product_id, data)

@router.delete("/{product_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(product_id: int, db: AsyncSession = Depends(get_session)) -> Response:
    await service.delete(db, product_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
