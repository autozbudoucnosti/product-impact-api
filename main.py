"""
Product Sustainability & Impact Assessment API.
Production-ready FastAPI app with API key auth, structured responses for AI agents.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from auth import validate_api_key
from logic import assess_impact
from rate_limit import check_rate_limit
from schemas import (
    AssessImpactRequest,
    CbamAnalysis,
    ImpactAssessmentResponse,
    ImpactBreakdown,
    MethodologyResponse,
)

app = FastAPI(
    title="Product Sustainability & Impact Assessment API",
    description="Assess product sustainability and environmental impact (CO2, water) for e-commerce and AI agents. Returns explainable, structured scores with human-readable explanations.",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication. Get your key from the provider.",
        }
    }
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ----- Methodology (GET) — static JSON for trust -----

METHODOLOGY_PAYLOAD = {
    "methodology_version": "v1.2.0",
    "description": "Enterprise indicative model for product sustainability. Score and CO2 are computed from material composition, weight, and origin-to-destination logistics. Not a certified LCA.",
    "total_sustainability_score": {
        "formula": "Score = 0.5 * Material + 0.3 * Logistics + 0.2 * Weight",
        "explanation": "Total sustainability score (0–100). Higher is better. Material and Logistics are scores 0–100; Weight term uses (100 - weight_penalty) so lighter products score higher.",
        "weights": {"material": 0.5, "logistics": 0.3, "weight": 0.2},
        "range": "0-100, higher is better",
    },
    "co2_estimate_kg": {
        "formula": "CO2 = Material_CO2 + Logistics_CO2",
        "components": [
            "Material CO2: sum over (weight_kg * share * material_CO2_per_kg) for each material",
            "Logistics CO2: weight_kg * (effective_distance_km / 1000) * kg_CO2_per_kg_per_1000_km * mode_multiplier",
        ],
        "mode_factors": {
            "sea": "circuitry 1.5x, CO2 multiplier 1x (baseline)",
            "road": "circuitry 1.2x, CO2 multiplier 5x",
            "rail": "circuitry 1.0x, CO2 multiplier 2x",
            "air": "circuitry 1.0x, CO2 multiplier 50x",
        },
        "unit": "kg CO2 equivalent",
        "note": "Uses 2026-aligned indicative emission factors per material and mode-adjusted logistics.",
    },
    "water_usage_liters": {
        "formula": "Sum over (weight_kg * share * water_liters_per_kg) for each material",
        "unit": "liters",
        "note": "Mainly from cultivation/processing (e.g. cotton). Synthetic materials use lower factors.",
    },
    "breakdown": {
        "material_score": "Weighted average of per-material sustainability scores (0-100). Higher = lower impact materials.",
        "logistics_score": "Score from origin-to-destination Great Circle distance; shorter = higher (0-100).",
        "weight_penalty": "Penalty from product weight; heavier products have higher weight_penalty. Used in score as (100 - weight_penalty) * 0.2.",
    },
    "disclaimer": "Indicative model-based estimate; not for regulatory CBAM filings. Results are not a certified Life Cycle Assessment (LCA) and must not be used as the sole basis for compliance or marketing claims.",
}


@app.get(
    "/v1/methodology",
    response_model=MethodologyResponse,
    summary="Get calculation methodology",
    description="Returns a JSON explanation of how sustainability scores and impact estimates (CO2, water, breakdown) are calculated. Use this to build trust and explain results to users or AI agents.",
)
def get_methodology() -> MethodologyResponse:
    return MethodologyResponse(
        methodology_version=METHODOLOGY_PAYLOAD["methodology_version"],
        description=METHODOLOGY_PAYLOAD["description"],
        total_sustainability_score=METHODOLOGY_PAYLOAD["total_sustainability_score"],
        co2_estimate_kg=METHODOLOGY_PAYLOAD["co2_estimate_kg"],
        water_usage_liters=METHODOLOGY_PAYLOAD["water_usage_liters"],
        breakdown=METHODOLOGY_PAYLOAD["breakdown"],
        disclaimer=METHODOLOGY_PAYLOAD["disclaimer"],
    )


# ----- Assess impact (POST) -----

@app.post(
    "/v1/assess-impact",
    response_model=ImpactAssessmentResponse,
    summary="Assess product sustainability and impact",
    description="Submit product details to receive an enterprise-grade response: score, confidence_level, CO2, explainable breakdown, CBAM analysis, and human-readable explanations. Rate limited per API key.",
)
def post_assess_impact(
    body: AssessImpactRequest,
    api_key: str = Security(validate_api_key),
) -> ImpactAssessmentResponse:
    if not check_rate_limit(api_key):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Max 5 per second per API key.",
        )
    result = assess_impact(
        product_name=body.product_name,
        material_composition=body.material_composition,
        weight_kg=body.weight_kg,
        origin_country=body.origin_country,
        destination_country=body.destination_country,
        shipping_mode=body.shipping_mode,
    )
    return ImpactAssessmentResponse(
        product_name=result["product_name"],
        total_sustainability_score=result["total_sustainability_score"],
        confidence_level=result["confidence_level"],
        co2_estimate_kg=result["co2_estimate_kg"],
        breakdown=ImpactBreakdown(**result["breakdown"]),
        cbam_analysis=CbamAnalysis(**result["cbam_analysis"]),
        explanation=result["explanation"],
        methodology_version=result["methodology_version"],
        disclaimer=result["disclaimer"],
    )


# ----- Demo / WOW endpoint (no auth) -----

DEMO_RESPONSE = {
    "product_name": "Eco-Friendly Bamboo T-Shirt",
    "total_sustainability_score": 87.5,
    "confidence_level": "medium",
    "co2_estimate_kg": 0.82,
    "breakdown": {
        "material_score": 85.0,
        "logistics_score": 78.0,
        "weight_penalty": 10.0,
    },
    "cbam_analysis": {
        "is_relevant": False,
        "reason": "Materials do not contain steel, aluminum, cement, fertilizer, hydrogen, or iron.",
    },
    "explanation": [
        "Bamboo grows fast but processing can be chemical-intensive.",
        "Sea freight is the most carbon-efficient shipping mode.",
        "Short shipping distance (<500 km) keeps logistics impact low.",
        "Lightweight product contributes to a better sustainability score.",
    ],
    "methodology_version": "v1.2.0",
    "disclaimer": "Indicative model-based estimate; not for regulatory CBAM filings.",
}


@app.get(
    "/demo/score",
    response_model=ImpactAssessmentResponse,
    summary="Demo: See a perfect score example",
    description="Returns a hardcoded, high-scoring example so users can instantly see what the API is capable of—no API key required.",
    tags=["Demo"],
)
def demo_score(product_name: Optional[str] = None) -> ImpactAssessmentResponse:
    """Moment of WOW endpoint: show a perfect example response."""
    response_data = DEMO_RESPONSE.copy()
    if product_name:
        response_data["product_name"] = product_name
    return ImpactAssessmentResponse(
        product_name=response_data["product_name"],
        total_sustainability_score=response_data["total_sustainability_score"],
        confidence_level=response_data["confidence_level"],
        co2_estimate_kg=response_data["co2_estimate_kg"],
        breakdown=ImpactBreakdown(**response_data["breakdown"]),
        cbam_analysis=CbamAnalysis(**response_data["cbam_analysis"]),
        explanation=response_data["explanation"],
        methodology_version=response_data["methodology_version"],
        disclaimer=response_data["disclaimer"],
    )


# ----- Health -----

@app.get("/health", tags=["Health"])
def health():
    """Health check for load balancers and monitoring."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
