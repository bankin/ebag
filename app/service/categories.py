from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.exceptions import ConflictError, NameConflictError, NotFoundError
from app.models.category import CategoryRead as Category, CategoryCreate, CategoryUpdate

# The parent relationship defaults to lazy loading (async-unsafe outside an
# await). Load it explicitly, one level deep, wherever a Category is read.
_WITH_PARENT = [selectinload(CategorySchema.parent)]


async def ensure_category_exists(db: AsyncSession, category_id: int, label: str = "Category") -> None:
    if await db.get(CategorySchema, category_id) is None:
        raise NotFoundError(f"{label} {category_id} not found")


async def create(db: AsyncSession, data: CategoryCreate) -> Category:
    db_category = CategorySchema(name=data.name, parent_id=data.parent_id)
    db.add(db_category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Category name already exists under this parent")

    return await get(db, db_category.id)


async def get(db: AsyncSession, category_id: int) -> Category:
    db_category = await db.get(
        CategorySchema, category_id, options=_WITH_PARENT, populate_existing=True
    )

    if db_category is None:
        raise NotFoundError(f"Category {category_id} not found")

    return Category.model_validate(db_category)


async def update(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    db_category = await db.get(
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
                await ensure_category_exists(db, new_parent_id, "Parent category")

            db_category.parent_id = new_parent_id

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Category name already exists under this parent")

    return await get(db, category_id)

async def delete(db: AsyncSession, category_id: int) -> None:
    db_category = await db.get(CategorySchema, category_id)

    if db_category is None:
        raise NotFoundError(f"Category {category_id} not found")

    child_count = await db.scalar(
        select(func.count()).select_from(CategorySchema).where(CategorySchema.parent_id == category_id)
    )
    product_count = await db.scalar(
        select(func.count()).select_from(ProductSchema).where(ProductSchema.category_id == category_id)
    )

    if child_count or product_count:
        raise ConflictError(
            f"Category {category_id} has {child_count} child categories and "
            f"{product_count} products and cannot be deleted"
        )

    await db.delete(db_category)
    await db.commit()
