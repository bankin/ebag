from fastapi import APIRouter

from app.models.product import Product

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/{product_id}")
def read(product_id: int):
    return {}

@router.post("/")
def create(product: Product):
    return product

@router.put("/{product_id}")
def update(product_id: int):
    return {}

@router.delete("/{product_id}")
def delete(product_id: int):
    return {}