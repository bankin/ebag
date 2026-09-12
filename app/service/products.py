from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.exceptions import NameConflictError, NotFoundError
from app.models.product import ProductRead as Product, ProductCreate, ProductUpdate
from app.service.categories import ensure_category_exists

# The category relationship defaults to lazy loading (async-unsafe outside an
# await). Load it explicitly, together with the category's own parent (needed
# for the nested CategoryRead shape), wherever a Product is read.
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
