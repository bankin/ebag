from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import storage
from app.config.exceptions import NotFoundError
from app.db.main import get_session
from app.db.schema.image import Image as ImageSchema
from app.models.image import ImageRead


class ImageService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def create(self, original_name: str, content_type: str | None, content: bytes) -> ImageRead:
        internal_name = storage.save_image(content_type, content)

        db_image = ImageSchema(original_name=original_name, internal_name=internal_name)
        self.db.add(db_image)

        await self.db.commit()

        return ImageRead.model_validate(db_image)

    async def get(self, image_id: int) -> ImageRead:
        db_image = await self.db.get(ImageSchema, image_id)

        if db_image is None:
            raise NotFoundError(f"Image {image_id} not found")

        return ImageRead.model_validate(db_image)

    async def ensure_exists(self, image_id: int, label: str = "Image") -> None:
        if await self.db.get(ImageSchema, image_id) is None:
            raise NotFoundError(f"{label} {image_id} not found")

    async def delete(self, image_id: int) -> None:
        db_image = await self.db.get(ImageSchema, image_id)

        if db_image is None:
            return

        internal_name = db_image.internal_name

        await self.db.delete(db_image)
        await self.db.commit()

        storage.delete_image(internal_name)
