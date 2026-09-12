import decimal

from pydantic import BaseModel

from app.models.category import CategoryRead


class Product(BaseModel):
    id: int
    title: str
    description: str | None = None
    image: str | None = None
    sku: str
    price: decimal.Decimal
    category: CategoryRead