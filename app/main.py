from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes import categories_internal, images_internal, products, products_internal

from app.db.main import verify_migrations
from app.exceptions import ConflictError, InvalidImageError, NameConflictError, NotFoundError
from app.storage import IMAGE_STORAGE_DIR, IMAGE_URL_PREFIX

@asynccontextmanager
async def lifespan(app_: FastAPI):
    verify_migrations()
    yield

app = FastAPI(lifespan=lifespan)

@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message})

@app.exception_handler(NameConflictError)
async def handle_name_conflict(request: Request, exc: NameConflictError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})

@app.exception_handler(ConflictError)
async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.message})

@app.exception_handler(InvalidImageError)
async def handle_invalid_image(request: Request, exc: InvalidImageError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.message})

app.include_router(products_internal.router)
app.include_router(products.router)
app.include_router(categories_internal.router)
app.include_router(images_internal.router)

app.mount(IMAGE_URL_PREFIX, StaticFiles(directory=IMAGE_STORAGE_DIR), name="images")
