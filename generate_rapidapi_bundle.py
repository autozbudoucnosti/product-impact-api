#!/usr/bin/env python3
"""
Generate a RapidAPI-ready OpenAPI bundle from openapi.json.
Injects x-rapidapi-info (tags) and examples for the assess-impact endpoint.
"""

import json
import sys
from pathlib import Path

OPENAPI_PATH = Path(__file__).parent / "openapi.json"
OUTPUT_PATH = Path(__file__).parent / "rapidapi_ready.json"

X_RAPIDAPI_INFO = {
    "tags": [
        "Sustainability",
        "CBAM",
        "Scope 3",
        "AI Agent Tool",
        "E-commerce",
    ],
}

ASSESS_IMPACT_REQUEST_EXAMPLE = {
    "summary": "Eco-friendly T-shirt (Recycled Cotton, 0.2 kg)",
    "description": "Sample request for a lightweight eco T-shirt made of recycled cotton.",
    "value": {
        "product_name": "Eco-friendly T-shirt",
        "material_composition": {"organic_cotton": 1.0},
        "weight_kg": 0.2,
        "origin_country": "Portugal",
        "destination_country": "Germany",
    },
}

ASSESS_IMPACT_RESPONSE_EXAMPLE = {
    "summary": "Eco-friendly T-shirt response",
    "description": "Example response with sustainability score, CO2, water, breakdown, and CBAM flag.",
    "value": {
        "total_sustainability_score": 72.4,
        "co2_estimate_kg": 1.89,
        "water_usage_liters": 3285.0,
        "breakdown": {
            "material_score": 73.0,
            "logistics_score": 70.0,
            "weight_impact": 90.0,
        },
        "methodology_version": "1.0.0-indicative",
        "cbam_relevant": False,
        "limitations": "This estimate is model-based and intended for internal assessment, not for final regulatory CBAM filings.",
    },
}


def main() -> None:
    if not OPENAPI_PATH.exists():
        print(f"Error: {OPENAPI_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(OPENAPI_PATH, encoding="utf-8") as f:
        spec = json.load(f)

    # 1. Inject x-rapidapi-info at root
    spec["x-rapidapi-info"] = X_RAPIDAPI_INFO

    # 2. Add examples for POST /v1/assess-impact
    post_spec = spec.get("paths", {}).get("/v1/assess-impact", {}).get("post", {})
    if not post_spec:
        print("Warning: POST /v1/assess-impact not found in spec.", file=sys.stderr)
    else:
        # Request body examples
        request_content = post_spec.get("requestBody", {}).get("content", {}).get("application/json", {})
        if request_content:
            request_content["examples"] = {
                "eco-friendly-tshirt": ASSESS_IMPACT_REQUEST_EXAMPLE,
            }
        # Response 200 example
        responses = post_spec.get("responses", {})
        resp_200 = responses.get("200", {}).get("content", {}).get("application/json", {})
        if resp_200:
            resp_200["examples"] = {
                "eco-friendly-tshirt": ASSESS_IMPACT_RESPONSE_EXAMPLE,
            }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    print(f"Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
