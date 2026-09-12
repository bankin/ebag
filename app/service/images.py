from sqlalchemy.ext.asyncio import AsyncSession

from app.config import storage
from app.config.exceptions import NotFoundError
from app.db.schema.image import Image as ImageSchema
from app.models.image import ImageRead


async def create(db: AsyncSession, original_name: str, content_type: str | None, content: bytes) -> ImageRead:
    internal_name = storage.save_image(content_type, content)

    db_image = ImageSchema(original_name=original_name, internal_name=internal_name)
    db.add(db_image)

    await db.commit()

    return ImageRead.model_validate(db_image)


async def get(db: AsyncSession, image_id: int) -> ImageRead:
    db_image = await db.get(ImageSchema, image_id)

    if db_image is None:
        raise NotFoundError(f"Image {image_id} not found")

    return ImageRead.model_validate(db_image)


async def ensure_image_exists(db: AsyncSession, image_id: int, label: str = "Image") -> None:
    if await db.get(ImageSchema, image_id) is None:
        raise NotFoundError(f"{label} {image_id} not found")


async def delete(db: AsyncSession, image_id: int) -> None:
    db_image = await db.get(ImageSchema, image_id)

    if db_image is None:
        return

    internal_name = db_image.internal_name

    await db.delete(db_image)
    await db.commit()

    storage.delete_image(internal_name)
