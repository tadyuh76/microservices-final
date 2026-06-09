from __future__ import annotations

from fastapi import FastAPI, HTTPException


PRODUCTS = [
    {"sku": "coffee", "name": "Iced Coffee", "category": "drinks", "price": 18000, "available": True},
    {"sku": "water", "name": "Bottled Water", "category": "drinks", "price": 8000, "available": True},
    {"sku": "tea", "name": "Peach Tea", "category": "drinks", "price": 16000, "available": True},
    {"sku": "sandwich", "name": "Chicken Sandwich", "category": "food", "price": 28000, "available": True},
    {"sku": "snack", "name": "Seaweed Snack", "category": "snacks", "price": 12000, "available": True},
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
async def list_products() -> list[dict[str, object]]:
    return PRODUCTS


@app.get("/products/{sku}")
async def get_product(sku: str) -> dict[str, object]:
    for product in PRODUCTS:
        if product["sku"] == sku:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

