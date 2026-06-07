from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query


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

app = FastAPI(
    title="PeakPick Catalog Service",
    version="0.1.0",
    description="Product browsing for the PeakPick demo.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "catalog-service"}


@app.get("/products")
async def list_products(category: str | None = Query(default=None)) -> list[dict[str, object]]:
    products = PRODUCTS
    if category:
        products = [product for product in products if product["category"] == category]
    return sorted(products, key=lambda product: (str(product["category"]), int(product["display_order"])))


@app.get("/categories")
async def list_categories() -> list[str]:
    return sorted({str(product["category"]) for product in PRODUCTS})


@app.get("/products/{sku}")
async def get_product(sku: str) -> dict[str, object]:
    for product in PRODUCTS:
        if product["sku"] == sku:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

