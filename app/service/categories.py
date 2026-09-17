from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.exceptions import ConflictError, NameConflictError, NotFoundError
from app.db.main import get_session
from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.models.category import CategoryCreate, CategoryUpdate
from app.models.category import CategoryRead as Category

# The parent relationship defaults to lazy loading (async-unsafe outside an
# await). Load it explicitly, one level deep, wherever a Category is read.
_WITH_PARENT = [selectinload(CategorySchema.parent)]


class CategoryService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def ensure_exists(self, category_id: int, label: str = "Category") -> None:
        if await self.db.get(CategorySchema, category_id) is None:
            raise NotFoundError(f"{label} {category_id} not found")

    async def _creates_cycle(self, category_id: int, new_parent_id: int) -> bool:
        """True if new_parent_id is category_id itself or one of its
        descendants — i.e. category_id is already an ancestor of
        new_parent_id, so setting new_parent_id as its parent would close a
        loop."""
        current_id = new_parent_id
        visited = set()

        while current_id is not None:
            if current_id == category_id:
                return True

            if current_id in visited:
                return False  # already-corrupt data; don't loop forever

            visited.add(current_id)
            current_id = await self.db.scalar(
                select(CategorySchema.parent_id).where(CategorySchema.id == current_id)
            )

        return False

    async def create(self, data: CategoryCreate) -> Category:
        db_category = CategorySchema(name=data.name, parent_id=data.parent_id)
        self.db.add(db_category)

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()

            raise NameConflictError("Category name already exists under this parent")

        return await self.get(db_category.id)

    async def get_all(self) -> list[Category]:
        db_categories = await self.db.scalars(select(CategorySchema).options(*_WITH_PARENT))

        return [Category.model_validate(c) for c in db_categories.all()]

    async def get(self, category_id: int) -> Category:
        db_category = await self.db.get(
            CategorySchema, category_id, options=_WITH_PARENT, populate_existing=True
        )

        if db_category is None:
            raise NotFoundError(f"Category {category_id} not found")

        return Category.model_validate(db_category)

    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        db_category = await self.db.get(
            CategorySchema, category_id, options=_WITH_PARENT, populate_existing=True
        )

        if db_category is None:
            raise NotFoundError(f"Category {category_id} not found")

        update_fields = data.model_dump(exclude_unset=True)

        if "name" in update_fields:
            db_category.name = update_fields["name"]

        if "parent_id" in update_fields:
            new_parent_id = update_fields["parent_id"]

            if new_parent_id != db_category.parent_id:
                if new_parent_id is not None:
                    await self.ensure_exists(new_parent_id, "Parent category")

                    if await self._creates_cycle(category_id, new_parent_id):
                        raise ConflictError(
                            f"Category {new_parent_id} is a descendant of {category_id}; "
                            "setting it as parent would create a cycle"
                        )

                db_category.parent_id = new_parent_id

        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()

            raise NameConflictError("Category name already exists under this parent")

        return await self.get(category_id)

    async def delete(self, category_id: int) -> None:
        db_category = await self.db.get(CategorySchema, category_id)

        if db_category is None:
            raise NotFoundError(f"Category {category_id} not found")

        child_count = await self.db.scalar(
            select(func.count())
            .select_from(CategorySchema)
            .where(CategorySchema.parent_id == category_id)
        )
        product_count = await self.db.scalar(
            select(func.count())
            .select_from(ProductSchema)
            .where(ProductSchema.category_id == category_id)
        )

        if child_count or product_count:
            raise ConflictError(
                f"Category {category_id} has {child_count} child categories and "
                f"{product_count} products and cannot be deleted"
            )

        await self.db.delete(db_category)
        await self.db.commit()
