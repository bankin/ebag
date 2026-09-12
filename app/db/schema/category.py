from sqlmodel import SQLModel, Field, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.schema.product import Product

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()

    parent_id: int | None = Field(default=None, nullable=True, foreign_key='category.id')

    parent: Category | None = Relationship(back_populates="children", sa_relationship_kwargs={"lazy": "select"})
    children: list['Category'] = Relationship(back_populates='parent')

    products: list['Product'] = Relationship(back_populates='category')