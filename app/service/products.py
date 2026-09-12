import decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.exceptions import NameConflictError, NotFoundError
from app.models.product import ProductRead as Product, ProductCreate, ProductUpdate
from app.service.categories import ensure_category_exists

_WITH_CATEGORY = [selectinload(ProductSchema.category).selectinload(CategorySchema.parent)]


async def create(db: AsyncSession, data: ProductCreate) -> Product:
    await ensure_category_exists(db, data.category_id)

    db_product = ProductSchema(
        title=data.title,
        description=data.description,
        sku=data.sku,
        price=data.price,
        category_id=data.category_id,
    )
    db.add(db_product)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Product SKU already exists")

    return await get(db, db_product.id)


async def get(db: AsyncSession, product_id: int) -> Product:
    db_product = await db.get(
        ProductSchema, product_id, options=_WITH_CATEGORY, populate_existing=True
    )

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    return Product.model_validate(db_product)


async def update(db: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
    db_product = await db.get(
        ProductSchema, product_id, options=_WITH_CATEGORY, populate_existing=True
    )

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    update_fields = data.model_dump(exclude_unset=True)

    if "category_id" in update_fields:
        new_category_id = update_fields.pop("category_id")

        if new_category_id != db_product.category_id:
            await ensure_category_exists(db, new_category_id)
            db_product.category_id = new_category_id

    for field, value in update_fields.items():
        setattr(db_product, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Product SKU already exists")

    return await get(db, product_id)


async def delete(db: AsyncSession, product_id: int) -> None:
    db_product = await db.get(ProductSchema, product_id)

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    await db.delete(db_product)
    await db.commit()


async def _resolve_category_ids(db: AsyncSession, category_name: str) -> list[int]:
    """Ids of every category matching this name (case-insensitive; more than
    one can match, since names are only unique per parent) plus all of their
    descendants, found via a recursive CTE walking parent_id -> id."""
    roots = (
        await db.scalars(
            select(CategorySchema.id).where(func.lower(CategorySchema.name) == category_name.lower())
        )
    ).all()

    if not roots:
        return []

    tree = (
        select(CategorySchema.id)
        .where(CategorySchema.id.in_(roots))
        .cte(name="category_tree", recursive=True)
    )
    tree = tree.union_all(
        select(CategorySchema.id).join(tree, CategorySchema.parent_id == tree.c.id)
    )

    return list((await db.scalars(select(tree.c.id))).all())


async def search(
    db: AsyncSession,
    *,
    name: str | None = None,
    sku: str | None = None,
    min_price: decimal.Decimal | None = None,
    max_price: decimal.Decimal | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Product]:
    stmt = select(ProductSchema).options(*_WITH_CATEGORY)

    if name:
        stmt = stmt.where(ProductSchema.title.ilike(f"%{name}%"))

    if sku:
        stmt = stmt.where(ProductSchema.sku.ilike(f"%{sku}%"))

    if min_price is not None:
        stmt = stmt.where(ProductSchema.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(ProductSchema.price <= max_price)

    if category:
        category_ids = await _resolve_category_ids(db, category)

        if not category_ids:
            return []

        stmt = stmt.where(ProductSchema.category_id.in_(category_ids))

    stmt = stmt.order_by(ProductSchema.id).limit(limit).offset(offset)

    db_products = (await db.scalars(stmt)).all()
    return [Product.model_validate(p) for p in db_products]
