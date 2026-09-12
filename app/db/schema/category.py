from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.db.util.timestamps import TimestampedModel

if TYPE_CHECKING:
    from app.db.schema.product import Product

class Category(TimestampedModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()

    parent_id: int | None = Field(default=None, nullable=True, foreign_key='category.id')

    parent: Category | None = Relationship(back_populates="children", sa_relationship_kwargs={"lazy": "select"})
    children: list['Category'] = Relationship(back_populates='parent')

    products: list['Product'] = Relationship(back_populates='category')