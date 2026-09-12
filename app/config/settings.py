from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://root:some@localhost:5432/ebag"
    alembic_database_url: str = "postgresql://root:some@localhost:5432/ebag"

    image_storage_dir: Path = Path("data/images")
    image_url_prefix: str = "/images"


settings = Settings()
