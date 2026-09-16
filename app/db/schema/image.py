from sqlmodel import Field

from app.config.storage import IMAGE_URL_PREFIX
from app.db.util.timestamps import TimestampedModel


class Image(TimestampedModel, table=True):
    __tablename__ = "images"

    id: int | None = Field(default=None, primary_key=True)
    original_name: str = Field()
    internal_name: str = Field(unique=True)

    @property
    def url(self) -> str:
        return f"{IMAGE_URL_PREFIX}/{self.internal_name}"
