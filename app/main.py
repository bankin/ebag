from fastapi import FastAPI

from app.routes import categories_internal, products, products_internal

app = FastAPI()

app.include_router(products.router)
app.include_router(products_internal.router)
app.include_router(categories_internal.router)