from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config.exceptions import register_exception_handlers
from app.config.storage import IMAGE_STORAGE_DIR, IMAGE_URL_PREFIX
from app.db.main import verify_migrations
from app.routes import categories_internal, images_internal, products, products_internal


@asynccontextmanager
async def lifespan(app_: FastAPI):
    verify_migrations()
    yield


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(products_internal.router)
app.include_router(products.router)
app.include_router(categories_internal.router)
app.include_router(images_internal.router)

app.mount(IMAGE_URL_PREFIX, StaticFiles(directory=IMAGE_STORAGE_DIR), name="images")
