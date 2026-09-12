from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.db.util.timestamps import TimestampedModel

if TYPE_CHECKING:
    from app.db.schema.product import Product

class Category(TimestampedModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()

    parent_id: int | None = Field(default=None, nullable=True, foreign_key='categories.id')

    parent: Optional['Category'] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"lazy": "selectin", "remote_side": "Category.id"},
    )
    children: list['Category'] = Relationship(back_populates='parent')

    products: list['Product'] = Relationship(back_populates='category')