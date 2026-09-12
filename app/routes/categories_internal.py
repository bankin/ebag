from fastapi import APIRouter

from app.models.category import Category

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/{category_id}")
def read(category_id: int):
    return {}

@router.post("/")
def create(category: Category):
    return category

@router.put("/{category_id}")
def update(category_id: int):
    return {}

@router.delete("/{category_id}")
def delete(category_id: int):
    return {}