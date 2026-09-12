"""Route-level tests for GET /products/search — exercised through the real
FastAPI app (get_session overridden to the in-memory test DB), covering
concerns that only exist at that layer: query param validation and request
wiring. Filtering/query logic itself is covered in tests/test_product_search.py.
"""

async def test_route_rejects_negative_limit(client):
    r = await client.get("/products/search", params={"limit": -1})

    assert r.status_code == 422


async def test_route_rejects_zero_limit(client):
    r = await client.get("/products/search", params={"limit": 0})

    assert r.status_code == 422


async def test_route_rejects_excessive_limit(client):
    r = await client.get("/products/search", params={"limit": 100000})

    assert r.status_code == 422


async def test_route_rejects_negative_offset(client):
    r = await client.get("/products/search", params={"offset": -1})

    assert r.status_code == 422


async def test_route_rejects_negative_min_price(client):
    r = await client.get("/products/search", params={"min_price": "-1"})

    assert r.status_code == 422


async def test_route_rejects_negative_max_price(client):
    r = await client.get("/products/search", params={"max_price": "-1"})

    assert r.status_code == 422


async def test_route_accepts_valid_params_end_to_end(client, seeded):
    r = await client.get("/products/search", params={"name": "app", "min_price": "0"})

    assert r.status_code == 200
    assert [p["sku"] for p in r.json()] == ["FRUIT-APPLE-1"]
