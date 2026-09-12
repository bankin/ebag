import decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.config.exceptions import NameConflictError, NotFoundError
from app.models.product import ProductRead as Product, ProductCreate, ProductUpdate
from app.service import images as images_service
from app.service.categories import ensure_category_exists

_LOAD_OPTIONS = [
    selectinload(ProductSchema.category).selectinload(CategorySchema.parent),
    selectinload(ProductSchema.image),
]

_LIKE_ESCAPE_CHAR = "\\"


def _escape_like(value: str) -> str:
    return (
        value.replace(_LIKE_ESCAPE_CHAR, _LIKE_ESCAPE_CHAR * 2)
        .replace("%", f"{_LIKE_ESCAPE_CHAR}%")
        .replace("_", f"{_LIKE_ESCAPE_CHAR}_")
    )


async def create(db: AsyncSession, data: ProductCreate) -> Product:
    await ensure_category_exists(db, data.category_id)

    if data.image_id is not None:
        await images_service.ensure_image_exists(db, data.image_id)

    db_product = ProductSchema(
        title=data.title,
        description=data.description,
        sku=data.sku,
        price=data.price,
        category_id=data.category_id,
        image_id=data.image_id,
    )
    db.add(db_product)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Product SKU already exists")

    return await get(db, db_product.id)


async def _image_still_in_use(db: AsyncSession, image_id: int, excluding_product_id: int) -> bool:
    count = await db.scalar(
        select(func.count())
        .select_from(ProductSchema)
        .where(ProductSchema.image_id == image_id, ProductSchema.id != excluding_product_id)
    )
    return bool(count)


async def get(db: AsyncSession, product_id: int) -> Product:
    db_product = await db.get(
        ProductSchema, product_id, options=_LOAD_OPTIONS, populate_existing=True
    )

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    return Product.model_validate(db_product)


async def update(db: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
    db_product = await db.get(
        ProductSchema, product_id, options=_LOAD_OPTIONS, populate_existing=True
    )

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    update_fields = data.model_dump(exclude_unset=True)

    if "category_id" in update_fields:
        new_category_id = update_fields.pop("category_id")

        if new_category_id != db_product.category_id:
            await ensure_category_exists(db, new_category_id)
            db_product.category_id = new_category_id

    # The old image (if any) is deleted once it's no longer referenced by
    # this product — but only after the product's own commit succeeds.
    old_image_id = None

    if "image_id" in update_fields:
        new_image_id = update_fields.pop("image_id")

        if new_image_id != db_product.image_id:
            if new_image_id is not None:
                await images_service.ensure_image_exists(db, new_image_id)

            old_image_id = db_product.image_id
            db_product.image_id = new_image_id

    for field, value in update_fields.items():
        setattr(db_product, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise NameConflictError("Product SKU already exists")

    if old_image_id is not None and not await _image_still_in_use(db, old_image_id, product_id):
        await images_service.delete(db, old_image_id)

    return await get(db, product_id)


async def delete(db: AsyncSession, product_id: int) -> None:
    db_product = await db.get(ProductSchema, product_id)

    if db_product is None:
        raise NotFoundError(f"Product {product_id} not found")

    old_image_id = db_product.image_id

    await db.delete(db_product)
    await db.commit()

    if old_image_id is not None and not await _image_still_in_use(db, old_image_id, product_id):
        await images_service.delete(db, old_image_id)


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
    stmt = select(ProductSchema).options(*_LOAD_OPTIONS)

    if name:
        stmt = stmt.where(ProductSchema.title.ilike(f"%{_escape_like(name)}%", escape=_LIKE_ESCAPE_CHAR))

    if sku:
        stmt = stmt.where(ProductSchema.sku.ilike(f"%{_escape_like(sku)}%", escape=_LIKE_ESCAPE_CHAR))

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
