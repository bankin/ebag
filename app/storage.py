import os
import uuid
from pathlib import Path

from app.exceptions import InvalidImageError

IMAGE_STORAGE_DIR = Path(os.environ.get("IMAGE_STORAGE_DIR", "data/images"))
IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_URL_PREFIX = "/images"

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

_EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def save_image(content_type: str | None, content: bytes) -> str:
    extension = _EXTENSION_BY_CONTENT_TYPE.get(content_type or "")
    if extension is None:
        raise InvalidImageError(
            f"Unsupported image type {content_type!r}; expected one of {sorted(_EXTENSION_BY_CONTENT_TYPE)}"
        )

    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise InvalidImageError(f"Image exceeds the {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB limit")

    if not content:
        raise InvalidImageError("Image file is empty")

    internal_name = f"{uuid.uuid4().hex}{extension}"
    (IMAGE_STORAGE_DIR / internal_name).write_bytes(content)

    return internal_name


def delete_image(internal_name: str | None) -> None:
    if not internal_name:
        return

    (IMAGE_STORAGE_DIR / Path(internal_name).name).unlink(missing_ok=True)
