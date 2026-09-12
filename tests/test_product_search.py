"""Unit tests for app.service.products.search() itself — no HTTP layer, no
FastAPI app involved. Route-level concerns (query param validation, wiring)
are covered separately in tests/test_product_search_api.py.
"""

import decimal

import pytest

from app.service import products as service


async def test_search_with_no_filters_returns_everything(db_session, seeded):
    results = await service.search(db_session)

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1", "VEG-CARROT-1"}


async def test_search_by_name_is_case_insensitive_partial_match(db_session, seeded):
    results = await service.search(db_session, name="app")

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_sku_partial_match(db_session, seeded):
    results = await service.search(db_session, sku="fruit-")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_price_range(db_session, seeded):
    results = await service.search(db_session, min_price=decimal.Decimal("1.00"), max_price=decimal.Decimal("1.80"))

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_price_range_is_inclusive(db_session, seeded):
    results = await service.search(db_session, min_price=decimal.Decimal("1.50"), max_price=decimal.Decimal("1.50"))

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_category_includes_products_in_child_categories(db_session, seeded):
    results = await service.search(db_session, category="Fruits")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_leaf_category_excludes_siblings(db_session, seeded):
    results = await service.search(db_session, category="Citrus")

    assert [p.sku for p in results] == ["FRUIT-ORANGE-1"]


async def test_search_by_category_name_is_case_insensitive(db_session, seeded):
    results = await service.search(db_session, category="fruits")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_unknown_category_returns_empty(db_session, seeded):
    results = await service.search(db_session, category="Does Not Exist")

    assert results == []


async def test_search_combines_filters(db_session, seeded):
    results = await service.search(db_session, category="Fruits", max_price=decimal.Decimal("1.80"))

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_respects_limit_and_offset(db_session, seeded):
    first_page = await service.search(db_session, limit=1, offset=0)
    second_page = await service.search(db_session, limit=1, offset=1)

    assert len(first_page) == 1
    assert len(second_page) == 1
    assert first_page[0].sku != second_page[0].sku


# --- invalid / adversarial params -------------------------------------------
#
# name/sku/category are never string-concatenated into SQL — they always go
# in as bound parameters (see .ilike(f"%{name}%"), which only builds the
# *value*, and func.lower(...) == category_name.lower()). These tests pin
# that down: injection-shaped input is treated as an inert literal search
# term, never breaks the query, and never affects data outside the request.

@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE products; --",
        "' OR '1'='1",
        "\" OR \"\"=\"",
        "%' UNION SELECT * FROM categories --",
    ],
)
async def test_search_by_name_with_injection_payload_is_treated_as_literal(db_session, seeded, payload):
    results = await service.search(db_session, name=payload)

    assert results == []


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE products; --",
        "' OR '1'='1",
    ],
)
async def test_search_by_sku_with_injection_payload_is_treated_as_literal(db_session, seeded, payload):
    results = await service.search(db_session, sku=payload)

    assert results == []


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE categories; --",
        "' OR '1'='1",
    ],
)
async def test_search_by_category_with_injection_payload_is_treated_as_literal(db_session, seeded, payload):
    results = await service.search(db_session, category=payload)

    assert results == []


async def test_search_survives_injection_attempts_and_still_works_afterward(db_session, seeded):
    await service.search(db_session, name="'; DROP TABLE products; --")
    await service.search(db_session, sku="'; DROP TABLE products; --")
    await service.search(db_session, category="'; DROP TABLE categories; --")

    results = await service.search(db_session, name="Apple")
    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_with_negative_min_price_matches_everything(db_session, seeded):
    results = await service.search(db_session, min_price=decimal.Decimal("-5"))

    assert len(results) == 3


async def test_search_with_negative_max_price_matches_nothing(db_session, seeded):
    results = await service.search(db_session, max_price=decimal.Decimal("-5"))

    assert results == []
