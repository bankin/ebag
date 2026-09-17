import decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models.product import ProductRead
from app.service.products import ProductService

router = APIRouter(prefix="/products", tags=["products"])

class SearchParams(BaseModel):
    name: str | None = None
    sku: str | None = None
    min_price: decimal.Decimal | None = Query(None, ge=0)
    max_price: decimal.Decimal | None = Query(None, ge=0)
    category: str | None = None
    limit: int = Query(50, ge=1, le=200)
    offset: int = Query(0, ge=0)

@router.get("/search", response_model=list[ProductRead])
async def search(
    search_query: Annotated[SearchParams, Query()],
    service: ProductService = Depends(ProductService),
) -> list[ProductRead]:
    return await service.search(
        name=search_query.name,
        sku=search_query.sku,
        min_price=search_query.min_price,
        max_price=search_query.max_price,
        category=search_query.category,
        limit=search_query.limit,
        offset=search_query.offset,
    )
