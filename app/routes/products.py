import decimal

from fastapi import APIRouter, Depends, Query

from app.models.product import ProductRead
from app.service.products import ProductService

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/search", response_model=list[ProductRead])
async def search(
    name: str | None = None,
    sku: str | None = None,
    min_price: decimal.Decimal | None = Query(None, ge=0),
    max_price: decimal.Decimal | None = Query(None, ge=0),
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ProductService = Depends(ProductService),
) -> list[ProductRead]:
    return await service.search(
        name=name,
        sku=sku,
        min_price=min_price,
        max_price=max_price,
        category=category,
        limit=limit,
        offset=offset,
    )
