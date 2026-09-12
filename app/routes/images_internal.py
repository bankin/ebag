from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.models.image import ImageRead
from app.service import images as service

router = APIRouter(
    prefix="/images",
    tags=["images"]
)

@router.post("/", response_model=ImageRead, status_code=status.HTTP_201_CREATED)
async def create(file: UploadFile = File(...), db: AsyncSession = Depends(get_session)) -> ImageRead:
    content = await file.read()
    return await service.create(db, file.filename or "upload", file.content_type, content)
