from fastapi import APIRouter

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/search")
def search():
    return []


@router.get("/{sku}")
def read_sku(sku: str):
    return {}
