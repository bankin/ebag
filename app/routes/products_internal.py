from fastapi import APIRouter, Depends, Response, status

from app.models.product import ProductCreate, ProductRead, ProductUpdate
from app.service.products import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id:int}", response_model=ProductRead)
async def read(
    product_id: int, service: ProductService = Depends(ProductService)
) -> ProductRead:
    return await service.get(product_id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create(
    data: ProductCreate, service: ProductService = Depends(ProductService)
) -> ProductRead:
    return await service.create(data)


@router.put("/{product_id:int}", response_model=ProductRead)
async def update(
    product_id: int,
    data: ProductUpdate,
    service: ProductService = Depends(ProductService),
) -> ProductRead:
    return await service.update(product_id, data)


@router.delete("/{product_id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    product_id: int, service: ProductService = Depends(ProductService)
) -> Response:
    await service.delete(product_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
