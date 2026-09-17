import decimal

import pytest

from app.service.products import ProductService
from tests.conftest import _make_product


async def test_search_with_no_filters_returns_everything(db_session, seeded):
    results = await ProductService(db_session).search()

    assert {p.sku for p in results} == {
        "FRUIT-APPLE-1",
        "FRUIT-ORANGE-1",
        "VEG-CARROT-1",
    }


async def test_search_by_name_is_case_insensitive_partial_match(db_session, seeded):
    results = await ProductService(db_session).search(name="app")

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_sku_partial_match(db_session, seeded):
    results = await ProductService(db_session).search(sku="fruit-")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_price_range(db_session, seeded):
    results = await ProductService(db_session).search(
        min_price=decimal.Decimal("1.00"), max_price=decimal.Decimal("1.80")
    )

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_price_range_is_inclusive(db_session, seeded):
    results = await ProductService(db_session).search(
        min_price=decimal.Decimal("1.50"), max_price=decimal.Decimal("1.50")
    )

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_by_category_includes_products_in_child_categories(
    db_session, seeded
):
    results = await ProductService(db_session).search(category="Fruits")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_leaf_category_excludes_siblings(db_session, seeded):
    results = await ProductService(db_session).search(category="Citrus")

    assert [p.sku for p in results] == ["FRUIT-ORANGE-1"]


async def test_search_by_category_name_is_case_insensitive(db_session, seeded):
    results = await ProductService(db_session).search(category="fruits")

    assert {p.sku for p in results} == {"FRUIT-APPLE-1", "FRUIT-ORANGE-1"}


async def test_search_by_unknown_category_returns_empty(db_session, seeded):
    results = await ProductService(db_session).search(category="Does Not Exist")

    assert results == []


async def test_search_combines_filters(db_session, seeded):
    results = await ProductService(db_session).search(
        category="Fruits", max_price=decimal.Decimal("1.80")
    )

    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_respects_limit_and_offset(db_session, seeded):
    first_page = await ProductService(db_session).search(limit=1, offset=0)
    second_page = await ProductService(db_session).search(limit=1, offset=1)

    assert len(first_page) == 1
    assert len(second_page) == 1
    assert first_page[0].sku != second_page[0].sku


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE products; --",
        "' OR '1'='1",
        '" OR ""="',
        "%' UNION SELECT * FROM categories --",
    ],
)
async def test_search_by_name_with_injection_payload_is_treated_as_literal(
    db_session, seeded, payload
):
    results = await ProductService(db_session).search(name=payload)

    assert results == []


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE products; --",
        "' OR '1'='1",
    ],
)
async def test_search_by_sku_with_injection_payload_is_treated_as_literal(
    db_session, seeded, payload
):
    results = await ProductService(db_session).search(sku=payload)

    assert results == []


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE categories; --",
        "' OR '1'='1",
    ],
)
async def test_search_by_category_with_injection_payload_is_treated_as_literal(
    db_session, seeded, payload
):
    results = await ProductService(db_session).search(category=payload)

    assert results == []


async def test_search_survives_injection_attempts_and_still_works_afterward(
    db_session, seeded
):
    await ProductService(db_session).search(name="'; DROP TABLE products; --")
    await ProductService(db_session).search(sku="'; DROP TABLE products; --")
    await ProductService(db_session).search(category="'; DROP TABLE categories; --")

    results = await ProductService(db_session).search(name="Apple")
    assert [p.sku for p in results] == ["FRUIT-APPLE-1"]


async def test_search_with_negative_min_price_matches_everything(db_session, seeded):
    results = await ProductService(db_session).search(min_price=decimal.Decimal(-5))

    assert len(results) == 3


async def test_search_with_negative_max_price_matches_nothing(db_session, seeded):
    results = await ProductService(db_session).search(max_price=decimal.Decimal(-5))

    assert results == []


async def test_search_by_name_treats_percent_as_literal(db_session, seeded):
    category_id = seeded["vegetables"].id
    await _make_product(db_session, "Save 10% Today", "LIKE-PCT-1", "1.00", category_id)
    await _make_product(db_session, "Save 10X Today", "LIKE-PCT-2", "1.00", category_id)

    results = await ProductService(db_session).search(name="10% Today")

    assert [p.sku for p in results] == ["LIKE-PCT-1"]


async def test_search_by_sku_treats_underscore_as_literal(db_session, seeded):
    category_id = seeded["vegetables"].id
    await _make_product(db_session, "A", "UNDER_SCORE-1", "1.00", category_id)
    await _make_product(db_session, "B", "UNDERXSCORE-1", "1.00", category_id)

    results = await ProductService(db_session).search(sku="UNDER_SCORE")

    assert [p.sku for p in results] == ["UNDER_SCORE-1"]
