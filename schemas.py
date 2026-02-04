"""
Pydantic v2 schemas for the Product Sustainability & Impact Assessment API.
All models include 'description' fields for AI agent and developer readability.
"""

from pydantic import BaseModel, Field


# ----- Request -----


class AssessImpactRequest(BaseModel):
    """Request body for the impact assessment endpoint."""

    product_name: str = Field(
        ...,
        description="Human-readable name of the product (e.g. 'Organic Cotton T-Shirt'). Used for labeling in responses.",
    )
    material_composition: dict[str, float] = Field(
        ...,
        description="Share of each material by weight, as decimals summing to 1.0. Example: {\"polyester\": 0.6, \"cotton\": 0.4}.",
    )
    weight_kg: float = Field(
        ...,
        gt=0,
        description="Product weight in kilograms. Must be greater than 0.",
    )
    origin_country: str = Field(
        ...,
        description="ISO-style country code or name where the product is produced (e.g. 'CN', 'Bangladesh'). Affects logistics emissions.",
    )
    destination_country: str = Field(
        ...,
        description="ISO-style country code or name where the product is delivered (e.g. 'US', 'Germany'). Affects logistics emissions.",
    )


# ----- Response: breakdown -----


class Breakdown(BaseModel):
    """Per-dimension scores and impacts for explainability."""

    material_score: float = Field(
        ...,
        description="Sustainability score for materials only (0–100). Higher = lower impact materials.",
    )
    logistics_score: float = Field(
        ...,
        description="Sustainability score for shipping from origin to destination (0–100). Higher = lower logistics impact.",
    )
    weight_impact: float = Field(
        ...,
        description="Contribution of product weight to overall impact (0–100). Heavier products reduce this score.",
    )


# ----- Response: main -----


class AssessImpactResponse(BaseModel):
    """Explainable, structured response for AI agents and e-commerce integrations."""

    total_sustainability_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall sustainability score from 0 to 100. Higher is better. Weighted combination of materials, logistics, and weight.",
    )
    co2_estimate_kg: float = Field(
        ...,
        ge=0,
        description="Estimated CO2 equivalent in kg for materials and logistics. Indicative, not certified.",
    )
    water_usage_liters: float = Field(
        ...,
        ge=0,
        description="Estimated water usage in liters (mainly from material production). Indicative.",
    )
    breakdown: Breakdown = Field(
        ...,
        description="Per-dimension scores: material_score, logistics_score, weight_impact. Use for explainability.",
    )
    methodology_version: str = Field(
        "1.0.0-indicative",
        description="Version of the calculation methodology. Use to track changes and build trust; 'indicative' means estimates, not certified LCA.",
    )
    cbam_relevant: bool = Field(
        False,
        description="True if the product contains CBAM-relevant materials (e.g. steel, aluminum, fertilizer). Indicates potential relevance for EU Carbon Border Adjustment Mechanism reporting; not for final regulatory use.",
    )
    limitations: str = Field(
        ...,
        description="Short disclaimer for agents: model-based, internal assessment only, not for final regulatory CBAM filings.",
    )


# ----- Methodology response -----


class MethodologyResponse(BaseModel):
    """JSON explanation of how scores and estimates are calculated (for transparency and trust)."""

    methodology_version: str = Field(
        "1.0.0-indicative",
        description="Current methodology version used by the API.",
    )
    description: str = Field(
        ...,
        description="Short summary of the methodology purpose and scope.",
    )
    total_sustainability_score: dict = Field(
        ...,
        description="How total_sustainability_score is computed (formula and weights).",
    )
    co2_estimate_kg: dict = Field(
        ...,
        description="How CO2 equivalent is estimated (materials + logistics).",
    )
    water_usage_liters: dict = Field(
        ...,
        description="How water usage is estimated (material-based).",
    )
    breakdown: dict = Field(
        ...,
        description="How material_score, logistics_score, and weight_impact are derived.",
    )
    disclaimer: str = Field(
        ...,
        description="Legal/disclaimer text: results are indicative, not certified LCA.",
    )
