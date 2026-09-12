import decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryRead


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    sku: str
    price: decimal.Decimal
    category: CategoryRead


class ProductCreate(BaseModel):
    title: str
    description: str | None = None
    sku: str
    price: decimal.Decimal = Field(ge=0)
    category_id: int
    image_id: int | None = None


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    sku: str | None = None
    price: decimal.Decimal | None = Field(default=None, ge=0)
    category_id: int | None = None
    image_id: int | None = None
