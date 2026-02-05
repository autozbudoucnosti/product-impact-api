"""
Shopify Product Sustainability Score — Example
Fetches a product (mocked), calls the Product Sustainability API, and prints a report.
"""

import os
import requests

# ---------------------------------------------------------------------------
# Configuration — set RAPIDAPI_KEY in env or replace below
# ---------------------------------------------------------------------------
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "YOUR_RAPIDAPI_KEY")
API_BASE_URL = "https://product-sustainability-api.p.rapidapi.com"  # Replace with your host


def mock_fetch_product_from_shopify(product_id: str) -> dict:
    """
    Simulates fetching a product from Shopify Admin API.
    Replace with real Shopify API calls when integrating.
    """
    # Mock product data — in production, use: GET /admin/api/2024-01/products/{id}.json
    mock_products = {
        "gid://shopify/Product/1001": {
            "id": "1001",
            "title": "Organic Cotton T-Shirt",
            "vendor": "EcoWear",
            "product_type": "Apparel",
            "variants": [{"id": "2001", "title": "Blue / M", "weight": 0.25, "weight_unit": "kg"}],
        },
        "gid://shopify/Product/1002": {
            "id": "1002",
            "title": "Recycled Polyester Jacket",
            "vendor": "GreenOuter",
            "product_type": "Outerwear",
            "variants": [{"id": "2002", "title": "Black / L", "weight": 0.8, "weight_unit": "kg"}],
        },
    }
    return mock_products.get(
        product_id,
        {
            "id": "999",
            "title": "Sample Product",
            "vendor": "Demo",
            "product_type": "General",
            "variants": [{"id": "2999", "title": "Default", "weight": 0.5, "weight_unit": "kg"}],
        },
    )


def get_sustainability_score(product_title: str, material: str = None, product_type: str = None) -> dict:
    """Calls the Product Sustainability API and returns the response."""
    # Adjust endpoint and payload to match your actual API
    url = f"{API_BASE_URL}/score"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "product-sustainability-api.p.rapidapi.com",
        "Content-Type": "application/json",
    }
    payload = {
        "product_name": product_title,
        "material": material or "mixed",
        "category": product_type,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def infer_material(product_type: str, title: str) -> str:
    """Simple heuristic to infer material from product type/title for demo."""
    t = (product_type or "").lower() + " " + (title or "").lower()
    if "cotton" in t or "organic" in t:
        return "cotton"
    if "polyester" in t or "recycled" in t:
        return "polyester"
    if "wool" in t or "jacket" in t:
        return "wool"
    return "mixed"


def _wrap(text: str, width: int) -> list[str]:
    """Wrap text into lines of at most `width` characters."""
    text = str(text)
    lines = []
    for i in range(0, len(text), width):
        lines.append(text[i : i + width].ljust(width))
    return lines or [""]


def print_sustainability_report(product: dict, api_response: dict) -> None:
    """Prints a formatted Sustainability Report to the terminal."""
    title = product.get("title", "Unknown Product")
    vendor = product.get("vendor", "—")
    product_type = product.get("product_type", "—")
    variant = (product.get("variants") or [{}])[0]
    weight = variant.get("weight", "—")
    weight_unit = variant.get("weight_unit", "kg")

    score = api_response.get("score") or api_response.get("sustainability_score") or "—"
    co2 = api_response.get("co2_kg") or api_response.get("carbon_footprint_kg") or api_response.get("co2e_kg") or "—"
    breakdown = api_response.get("breakdown") or api_response.get("breakdown_text") or "No breakdown available."

    pad = 56
    breakdown_lines = _wrap(breakdown, pad)

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  🌿  S U S T A I N A B I L I T Y   R E P O R T  🌿           ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Product    {str(title)[:44]:<44}  ║")
    print(f"║  Vendor     {str(vendor)[:44]:<44}  ║")
    print(f"║  Type       {str(product_type)[:44]:<44}  ║")
    print(f"║  Weight     {str(weight)} {str(weight_unit):<41}  ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Sustainability Score   {str(score):<34}  ║")
    print(f"║  CO₂ (kg)               {str(co2):<34}  ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Breakdown:                                                 ║")
    for line in breakdown_lines[:6]:
        print(f"║    {line:<54}  ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")


def main():
    # 1) Mock fetch from Shopify
    product_id = "gid://shopify/Product/1001"
    product = mock_fetch_product_from_shopify(product_id)
    material = infer_material(product.get("product_type"), product.get("title"))

    # 2) Call your Product Sustainability API
    api_response = get_sustainability_score(
        product_title=product["title"],
        material=material,
        product_type=product.get("product_type"),
    )

    # 3) Print report
    print_sustainability_report(product, api_response)


if __name__ == "__main__":
    main()
