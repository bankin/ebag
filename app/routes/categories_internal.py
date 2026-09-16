from fastapi import APIRouter, Depends, Response, status

from app.models.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.service.categories import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/{category_id}", response_model=CategoryRead)
async def read(
    category_id: int, service: CategoryService = Depends(CategoryService)
) -> CategoryRead:
    return await service.get(category_id)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate, service: CategoryService = Depends(CategoryService)
) -> CategoryRead:
    return await service.create(data)


@router.put("/{category_id}", response_model=CategoryRead)
async def update(
    category_id: int,
    data: CategoryUpdate,
    service: CategoryService = Depends(CategoryService),
) -> CategoryRead:
    return await service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    category_id: int, service: CategoryService = Depends(CategoryService)
) -> Response:
    await service.delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
