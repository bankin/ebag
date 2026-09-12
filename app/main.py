from fastapi import FastAPI

from app.routes import categories_internal, products, products_internal

from app.db.main import init_db

app = FastAPI()

app.include_router(products.router)
app.include_router(products_internal.router)
app.include_router(categories_internal.router)

init_db()