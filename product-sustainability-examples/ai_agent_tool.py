"""
AI Agent Tool — Product Carbon Footprint
For use with LangChain, LlamaIndex, or any AI agent that can call Python tools.
Exposes get_product_carbon_footprint(product_name, material) and returns the
API breakdown text so the agent can explain it to the user.
"""

import os
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "YOUR_RAPIDAPI_KEY")
API_BASE_URL = "https://product-sustainability-api.p.rapidapi.com"  # Replace with your host


def get_product_carbon_footprint(
    product_name: str,
    material: Optional[str] = None,
    category: Optional[str] = None,
) -> str:
    """
    Get the carbon footprint breakdown for a product.

    Call this from your AI agent (e.g. LangChain tool) when the user asks
    about a product's environmental impact. The returned breakdown text
    is suitable for the model to quote or paraphrase in its answer.

    Args:
        product_name: Name or description of the product (e.g. "Organic Cotton T-Shirt").
        material: Optional primary material (e.g. "cotton", "polyester", "mixed").
        category: Optional product category (e.g. "Apparel", "Electronics").

    Returns:
        Human-readable breakdown text explaining the carbon footprint.
        On API or network errors, returns an error message string.
    """
    url = f"{API_BASE_URL}/score"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "product-sustainability-api.p.rapidapi.com",
        "Content-Type": "application/json",
    }
    payload = {
        "product_name": product_name,
        "material": material or "mixed",
        "category": category,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Unable to fetch carbon footprint: {e!s}"

    breakdown = data.get("breakdown") or data.get("breakdown_text")
    if breakdown:
        return breakdown

    # Fallback: build a short summary from common response fields
    score = data.get("score") or data.get("sustainability_score")
    co2 = data.get("co2_kg") or data.get("carbon_footprint_kg") or data.get("co2e_kg")
    parts = []
    if score is not None:
        parts.append(f"Sustainability score: {score}.")
    if co2 is not None:
        parts.append(f"Estimated carbon footprint: {co2} kg CO₂e.")
    return " ".join(parts) if parts else "No breakdown available from the API."


# ---------------------------------------------------------------------------
# LangChain tool (optional)
# ---------------------------------------------------------------------------
def get_langchain_tool():
    """Return a LangChain tool that wraps get_product_carbon_footprint."""
    try:
        from langchain_core.tools import tool
    except ImportError:
        raise ImportError("Install langchain-core to use get_langchain_tool(): pip install langchain-core")

    @tool
    def product_carbon_footprint(product_name: str, material: str = "mixed") -> str:
        """Get the carbon footprint breakdown for a product. Use when the user asks about environmental impact, CO2, or sustainability of a product."""
        return get_product_carbon_footprint(product_name=product_name, material=material)

    return product_carbon_footprint


if __name__ == "__main__":
    # Quick test
    result = get_product_carbon_footprint("Organic Cotton T-Shirt", material="cotton")
    print("Breakdown:", result)
