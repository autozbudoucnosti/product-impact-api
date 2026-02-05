"""
Pydantic v2 schemas for the Product Sustainability & Impact Assessment API.
Enterprise-grade, nested, and explainable for AI agents.
"""

from pydantic import BaseModel, Field


# ----- Request -----


class AssessImpactRequest(BaseModel):
    """Request body for the impact assessment endpoint."""

    product_name: str = Field(
        ...,
        description="Human-readable name of the product (e.g. 'Organic Cotton T-Shirt'). Echoed in response.",
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
    shipping_mode: str = Field(
        "sea",
        description="Shipping mode: 'sea', 'air', 'road', or 'rail'. Affects CO2 calculation with circuitry factors and mode multipliers.",
    )


# ----- Response: breakdown (explainable for AI agents) -----


class ImpactBreakdown(BaseModel):
    """Per-dimension scores so agents can explain why a score is low or high."""

    material_score: float = Field(
        ...,
        description="Sustainability score for materials only (0–100). Higher = lower impact materials.",
    )
    logistics_score: float = Field(
        ...,
        description="Sustainability score for shipping from origin to destination (0–100). Higher = lower logistics impact.",
    )
    weight_penalty: float = Field(
        ...,
        description="Penalty from product weight; heavier products add to this. Used in total score calculation.",
    )


# ----- Response: CBAM analysis (enterprise trigger for EU buyers) -----


class CbamAnalysis(BaseModel):
    """CBAM relevance and human-readable reason for regulatory awareness."""

    is_relevant: bool = Field(
        ...,
        description="True if the product contains CBAM-relevant materials (steel, aluminum, cement, fertilizer, hydrogen, iron).",
    )
    reason: str = Field(
        ...,
        description="Short explanation: either which materials triggered CBAM relevance or that none were found.",
    )


# ----- Response: main (enterprise nested structure) -----


class ImpactAssessmentResponse(BaseModel):
    """Enterprise-grade, nested, explainable response for AI agents and e-commerce."""

    product_name: str = Field(
        ...,
        description="Product name as submitted; echoed for context.",
    )
    total_sustainability_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall sustainability score from 0 to 100. Higher is better. Score = 0.5*Material + 0.3*Logistics + 0.2*Weight.",
    )
    confidence_level: str = Field(
        "medium",
        description="Confidence in the estimate (e.g. low, medium, high). Currently medium for model-based estimates.",
    )
    co2_estimate_kg: float = Field(
        ...,
        ge=0,
        description="Estimated CO2 equivalent in kg for materials and logistics. Indicative, not certified.",
    )
    breakdown: ImpactBreakdown = Field(
        ...,
        description="Per-dimension scores so agents can explain e.g. 'The score is low because logistics_score is low.'",
    )
    cbam_analysis: CbamAnalysis = Field(
        ...,
        description="Whether the product is CBAM-relevant and why; key for European enterprise buyers.",
    )
    explanation: list[str] = Field(
        default_factory=list,
        description="Human-readable explanations for the score. AI agents can surface these to users to explain why the score is high or low.",
    )
    methodology_version: str = Field(
        "v1.2.0",
        description="Version of the calculation methodology. Use to track changes and build trust.",
    )
    disclaimer: str = Field(
        ...,
        description="Legal disclaimer: indicative model-based estimate; not for regulatory CBAM filings.",
    )


# Backward compatibility
AssessImpactResponse = ImpactAssessmentResponse
Breakdown = ImpactBreakdown


# ----- Methodology response -----


class MethodologyResponse(BaseModel):
    """Static JSON explaining how scores are calculated (for transparency and trust)."""

    methodology_version: str = Field(
        "v1.2.0",
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
        description="How material_score, logistics_score, and weight_penalty are derived.",
    )
    disclaimer: str = Field(
        ...,
        description="Legal/disclaimer text: results are indicative, not certified LCA.",
    )
