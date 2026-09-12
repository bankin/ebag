import decimal

from sqlmodel import SQLModel, Field, Relationship

from app.db.schema.category import Category

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field()
    description: str = Field(nullable=True)
    image_url: str = Field(nullable=True)
    sku: str = Field()
    price: decimal.Decimal = Field()

    category_id: int = Field(default=None, foreign_key='category.id')
    category: Category = Relationship(back_populates='products')