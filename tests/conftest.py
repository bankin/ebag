import decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

# Import both schema modules so their tables are registered on
# SQLModel.metadata before create_all() runs below.
from app.db.schema import category, product  # noqa: F401
from app.db.schema.category import Category as CategorySchema
from app.db.schema.product import Product as ProductSchema
from app.db.main import get_session
from app.main import app


@pytest.fixture
async def db_session():
    # A fresh in-memory SQLite DB per test — fast, isolated, and (via
    # SQLAlchemy's WITH RECURSIVE / ilike() emulation) compatible enough with
    # the queries under test that we don't need a real Postgres for this.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session):
    # An HTTP client for the real app, with get_session overridden to use
    # the in-memory test DB above instead of the real Postgres — lets us
    # test route-level behavior (query param validation) without a live DB.
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _make_category(db: AsyncSession, name: str, parent_id: int | None = None) -> CategorySchema:
    db_category = CategorySchema(name=name, parent_id=parent_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def _make_product(db: AsyncSession, title: str, sku: str, price: str, category_id: int) -> ProductSchema:
    db_product = ProductSchema(title=title, sku=sku, price=decimal.Decimal(price), category_id=category_id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@pytest.fixture
async def seeded(db_session: AsyncSession) -> dict[str, object]:
    # Shared fixture data for product search tests, service- and route-level
    # alike:
    #   Fruits (root)
    #     Citrus (child)
    #   Vegetables (root, no children)
    fruits = await _make_category(db_session, "Fruits")
    citrus = await _make_category(db_session, "Citrus", parent_id=fruits.id)
    vegetables = await _make_category(db_session, "Vegetables")

    apple = await _make_product(db_session, "Apple", "FRUIT-APPLE-1", "1.50", fruits.id)
    orange = await _make_product(db_session, "Orange", "FRUIT-ORANGE-1", "2.00", citrus.id)
    carrot = await _make_product(db_session, "Carrot", "VEG-CARROT-1", "0.75", vegetables.id)

    return {
        "fruits": fruits,
        "citrus": citrus,
        "vegetables": vegetables,
        "apple": apple,
        "orange": orange,
        "carrot": carrot,
    }
