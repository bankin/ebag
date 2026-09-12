import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import categories_internal, products, products_internal

from app.db.main import verify_migrations

@asynccontextmanager
async def lifespan(app_: FastAPI):
    verify_migrations()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(products.router)
app.include_router(products_internal.router)
app.include_router(categories_internal.router)
