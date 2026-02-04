"""
HTTP client for the Product Sustainability & Impact Assessment API.
Handles X-API-Key header and wraps assess-impact and methodology endpoints.
"""

from __future__ import annotations

import os
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore


def _normalize_material_key(name: str) -> str:
    """Turn 'Recycled Cotton' -> 'recycled_cotton' for API."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


class ImpactResult:
    """Result of an impact assessment. Use .co2_estimate for quick access."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.product_name: str = data.get("product_name", "")
        self.total_sustainability_score: float = data["total_sustainability_score"]
        self.confidence_level: str = data.get("confidence_level", "medium")
        self.co2_estimate_kg: float = data["co2_estimate_kg"]
        self.co2_estimate: float = data["co2_estimate_kg"]  # alias
        self.water_usage_liters: float | None = data.get("water_usage_liters")
        self.breakdown: dict[str, float] = data["breakdown"]
        self.methodology_version: str = data.get("methodology_version", "v1.2.0-beta")
        cbam = data.get("cbam_analysis") or {}
        self.cbam_relevant: bool = cbam.get("is_relevant", data.get("cbam_relevant", False))
        self.cbam_reason: str = cbam.get("reason", "")
        self.disclaimer: str = data.get("disclaimer", data.get("limitations", ""))
        self.limitations: str = self.disclaimer  # alias

    def __repr__(self) -> str:
        return f"ImpactResult(score={self.total_sustainability_score}, co2_kg={self.co2_estimate_kg})"


class EcoClient:
    """
    Client for the Product Sustainability & Impact Assessment API.
    Set X-API-Key automatically. Get your API key from RapidAPI.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = (api_key or os.environ.get("ECOSCORE_API_KEY", "")).strip()
        if not self._api_key:
            raise ValueError(
                "API key required. Pass api_key= or set ECOSCORE_API_KEY. "
                "Get your key: https://rapidapi.com/..."
            )
        self._base_url = (base_url or os.environ.get("ECOSCORE_BASE_URL", "")).rstrip("/")
        if not self._base_url:
            raise ValueError(
                "Base URL required. Pass base_url= or set ECOSCORE_BASE_URL to your API root (e.g. https://yourapp.railway.app)."
            )
        self._headers = {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if httpx is None:
            raise ImportError("ecoscore-sdk requires httpx. Install with: pip install httpx")
        url = f"{self._base_url}{path}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.request(method, url, headers=self._headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    def assess_impact(
        self,
        product: str,
        material: str | dict[str, float],
        weight_kg: float = 0.2,
        origin_country: str = "CN",
        destination_country: str = "US",
    ) -> ImpactResult:
        """
        Assess sustainability impact for a product.

        :param product: Product name (e.g. "T-Shirt").
        :param material: Single material name (e.g. "Cotton") or dict (e.g. {"cotton": 0.6, "polyester": 0.4}).
        :param weight_kg: Weight in kg (default 0.2).
        :param origin_country: Production country (default "CN").
        :param destination_country: Delivery country (default "US").
        :return: ImpactResult with .co2_estimate, .water_usage_liters, .total_sustainability_score, etc.
        """
        if isinstance(material, str):
            key = _normalize_material_key(material)
            material_composition = {key: 1.0}
        else:
            material_composition = {_normalize_material_key(k): v for k, v in material.items()}
        payload = {
            "product_name": product,
            "material_composition": material_composition,
            "weight_kg": weight_kg,
            "origin_country": origin_country,
            "destination_country": destination_country,
        }
        data = self._request("POST", "/v1/assess-impact", json=payload)
        return ImpactResult(data)

    def get_methodology(self) -> dict[str, Any]:
        """Get the calculation methodology (formulas, weights, disclaimer)."""
        return self._request("GET", "/v1/methodology")
