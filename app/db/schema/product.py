import decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.db.schema.category import Category
from app.db.util.timestamps import TimestampedModel

if TYPE_CHECKING:
    from app.db.schema.image import Image


class Product(TimestampedModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field()
    description: str = Field(nullable=True)
    sku: str = Field()
    price: decimal.Decimal = Field()

    category_id: int = Field(default=None, foreign_key="categories.id")
    category: Category = Relationship(back_populates="products")

    image_id: int | None = Field(default=None, foreign_key="images.id", nullable=True)
    image: Image | None = Relationship()

    @property
    def image_url(self) -> str | None:
        return self.image.url if self.image else None
