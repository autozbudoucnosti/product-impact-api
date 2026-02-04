"""
Product Sustainability & Impact Assessment API.
Production-ready FastAPI app with API key auth, structured responses for AI agents.
"""

from fastapi import FastAPI, HTTPException, Security
from fastapi.openapi.utils import get_openapi

from auth import validate_api_key
from logic import assess_impact
from rate_limit import check_rate_limit
from schemas import (
    AssessImpactRequest,
    AssessImpactResponse,
    Breakdown,
    MethodologyResponse,
)

app = FastAPI(
    title="Product Sustainability & Impact Assessment API",
    description="Assess product sustainability and environmental impact (CO2, water) for e-commerce and AI agents. Returns explainable, structured scores.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


# ----- Methodology (GET) -----

METHODOLOGY_PAYLOAD = {
    "methodology_version": "1.0.0-indicative",
    "description": "Indicative sustainability scoring and impact estimates for products based on material composition, weight, and origin-to-destination logistics. Not a certified LCA.",
    "total_sustainability_score": {
        "formula": "0.50 * material_score + 0.30 * logistics_score + 0.20 * weight_impact",
        "weights": {"material": 0.5, "logistics": 0.3, "weight": 0.2},
        "range": "0-100, higher is better",
    },
    "co2_estimate_kg": {
        "components": [
            "Material CO2: sum over (weight_kg * share * material_CO2_per_kg) for each material",
            "Logistics CO2: weight_kg * (distance_km / 1000) * kg_CO2_per_kg_per_1000_km",
        ],
        "unit": "kg CO2 equivalent",
        "note": "Uses indicative emission factors per material and distance-based logistics.",
    },
    "water_usage_liters": {
        "formula": "Sum over (weight_kg * share * water_liters_per_kg) for each material",
        "unit": "liters",
        "note": "Mainly from cultivation/processing (e.g. cotton). Synthetic materials use lower factors.",
    },
    "breakdown": {
        "material_score": "Weighted average of per-material sustainability scores (0-100).",
        "logistics_score": "Score from origin-to-destination distance; shorter = higher (0-100).",
        "weight_impact": "Score from product weight; lighter = higher (0-100).",
    },
    "disclaimer": "Results are indicative estimates only. They are not a certified Life Cycle Assessment (LCA) and must not be used as the sole basis for compliance or marketing claims. Methodology may change; check methodology_version.",
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
    response_model=AssessImpactResponse,
    summary="Assess product sustainability and impact",
    description="Submit product details (name, material composition, weight, origin and destination countries) to receive a structured sustainability score, CO2 estimate, water usage, breakdown, CBAM relevance, and limitations. Rate limited per API key.",
)
def post_assess_impact(
    body: AssessImpactRequest,
    api_key: str = Security(validate_api_key),
) -> AssessImpactResponse:
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
    )
    return AssessImpactResponse(
        total_sustainability_score=result["total_sustainability_score"],
        co2_estimate_kg=result["co2_estimate_kg"],
        water_usage_liters=result["water_usage_liters"],
        breakdown=Breakdown(**result["breakdown"]),
        methodology_version=result["methodology_version"],
        cbam_relevant=result["cbam_relevant"],
        limitations=result["limitations"],
    )


# ----- Health -----

@app.get("/health", tags=["Health"])
def health():
    """Health check for load balancers and monitoring."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
