from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.schema.category import Category as CategorySchema
from app.exceptions import NameConflictError, NotFoundError
from app.models.category import CategoryRead as Category, CategoryCreate, CategoryUpdate

# The parent relationship defaults to lazy loading (async-unsafe outside an
# await). Load it explicitly, one level deep, wherever a Category is read.
_WITH_PARENT = [selectinload(CategorySchema.parent)]


async def create(db: AsyncSession, data: CategoryCreate) -> Category:
    db_category = CategorySchema(name=data.name, parent_id=data.parent_id)
    db.add(db_category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Category name already exists under this parent")

    await db.refresh(db_category, attribute_names=["parent"])
    return Category.model_validate(db_category)


async def get(db: AsyncSession, category_id: int) -> Category:
    db_category = await db.get(CategorySchema, category_id, options=_WITH_PARENT)

    if db_category is None:
        raise NotFoundError(f"Category {category_id} not found")

    return Category.model_validate(db_category)


async def update(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    db_category = await db.get(CategorySchema, category_id, options=_WITH_PARENT)

    if db_category is None:
        raise NotFoundError(f"Category {category_id} not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_category, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Category name already exists under this parent")

    await db.refresh(db_category, attribute_names=["parent"])
    return Category.model_validate(db_category)


async def delete(db: AsyncSession, category_id: int) -> None:
    db_category = await db.get(CategorySchema, category_id)

    if db_category is None:
        raise NotFoundError(f"Category {category_id} not found")

    await db.delete(db_category)
    await db.commit()
