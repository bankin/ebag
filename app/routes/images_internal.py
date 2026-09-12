from fastapi import APIRouter, Depends, File, UploadFile, status

from app.models.image import ImageRead
from app.service.images import ImageService

router = APIRouter(
    prefix="/images",
    tags=["images"]
)

@router.post("/", response_model=ImageRead, status_code=status.HTTP_201_CREATED)
async def create(file: UploadFile = File(...), service: ImageService = Depends(ImageService)) -> ImageRead:
    content = await file.read()
    return await service.create(file.filename or "upload", file.content_type, content)
