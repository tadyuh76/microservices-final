from fastapi.testclient import TestClient

from services.catalog_service.main import app


client = TestClient(app)


def test_products_include_member3_demo_fields() -> None:
    response = client.get("/products")

    assert response.status_code == 200
    product = response.json()[0]
    assert {"sku", "name", "category", "price", "available"}.issubset(product)
    assert product["sku"]
    assert product["price"] > 0


def test_products_can_be_filtered_by_category() -> None:
    response = client.get("/products?category=drinks")

    assert response.status_code == 200
    products = response.json()
    assert products
    assert {product["category"] for product in products} == {"drinks"}


def test_categories_endpoint_returns_unique_categories() -> None:
    response = client.get("/categories")

    assert response.status_code == 200
    assert response.json() == ["drinks", "food", "snacks"]
