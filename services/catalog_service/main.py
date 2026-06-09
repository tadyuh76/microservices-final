from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException, Query

from shared.logging import configure_logging, install_api_logging
from shared.settings import get_settings


PRODUCTS = [
    {
        "sku": "coffee",
        "name": "Iced Coffee",
        "category": "drinks",
        "price": 18000,
        "available": True,
        "prep_time_minutes": 2,
        "display_order": 1,
    },
    {
        "sku": "water",
        "name": "Bottled Water",
        "category": "drinks",
        "price": 8000,
        "available": True,
        "prep_time_minutes": 1,
        "display_order": 2,
    },
    {
        "sku": "tea",
        "name": "Peach Tea",
        "category": "drinks",
        "price": 16000,
        "available": True,
        "prep_time_minutes": 2,
        "display_order": 3,
    },
    {
        "sku": "sandwich",
        "name": "Chicken Sandwich",
        "category": "food",
        "price": 28000,
        "available": True,
        "prep_time_minutes": 5,
        "display_order": 1,
    },
    {
        "sku": "snack",
        "name": "Seaweed Snack",
        "category": "snacks",
        "price": 12000,
        "available": True,
        "prep_time_minutes": 1,
        "display_order": 1,
    },
]
settings = get_settings("catalog-service")
logger = configure_logging(settings.service_name)


def _database_enabled() -> bool:
    return bool(settings.database_url)


async def _list_products_from_db(category: str | None = None) -> list[dict[str, object]]:
    return await asyncio.to_thread(_list_products_from_db_sync, category)


def _list_products_from_db_sync(category: str | None = None) -> list[dict[str, object]]:
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        if category:
            rows = conn.execute(
                """
                SELECT sku, name, category, price, available, prep_time_minutes, display_order
                FROM products
                WHERE category = %s
                ORDER BY category, display_order
                """,
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT sku, name, category, price, available, prep_time_minutes, display_order
                FROM products
                ORDER BY category, display_order
                """
            ).fetchall()
        return [dict(row) for row in rows]

app = FastAPI(
    title="PeakPick Catalog Service",
    version="0.1.0",
    description="Product browsing for the PeakPick demo.",
)
install_api_logging(app, logger, settings.service_name)


@app.get("/health")
async def health() -> dict[str, object]:
    return {"status": "ok", "service": settings.service_name, "database_enabled": _database_enabled()}


@app.get("/products")
async def list_products(category: str | None = Query(default=None)) -> list[dict[str, object]]:
    if _database_enabled():
        return await _list_products_from_db(category)
    products = PRODUCTS
    if category:
        products = [product for product in products if product["category"] == category]
    return sorted(products, key=lambda product: (str(product["category"]), int(product["display_order"])))


@app.get("/categories")
async def list_categories() -> list[str]:
    if _database_enabled():
        return sorted({str(product["category"]) for product in await _list_products_from_db()})
    return sorted({str(product["category"]) for product in PRODUCTS})


@app.get("/products/{sku}")
async def get_product(sku: str) -> dict[str, object]:
    products = await _list_products_from_db() if _database_enabled() else PRODUCTS
    for product in products:
        if product["sku"] == sku:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
