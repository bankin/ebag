from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config.settings import settings
from app.db.schema import product, category, image

engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=True)

# def init_db() -> None:
#     SQLModel.metadata.create_all(engine)

# FIXME
def verify_migrations():
    return True
#     alembic_cfg = Config("alembic.ini")
#     current != head check


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session