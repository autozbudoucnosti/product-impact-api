# Product Sustainability & Impact Assessment API

## 🔑 Getting Started

To use this client, you need an API Key.
**[👉 Click here to get your Free API Key on RapidAPI](https://web-production-a1f91.up.railway.app)**

---

**Production-ready API for e-commerce developers and AI agents** to assess product sustainability and environmental impact. Returns explainable, structured scores (CO2, water, breakdown) suitable for storefronts, dashboards, and AI reasoning.

---

## Features

- **POST `/v1/assess-impact`** — Submit product details; get a 0–100 sustainability score, CO2 estimate (kg), water usage (L), and a per-dimension breakdown.
- **GET `/v1/methodology`** — JSON explanation of how scores are calculated (for transparency and trust).
- **API Key authentication** — Header-based (`X-API-Key`) for secure access.
- **Structured, AI-friendly responses** — All fields documented; ideal for agents and integrations.

---

## Quick Start

### 1. Install and run

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Docs:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **OpenAPI JSON:** http://localhost:8000/openapi.json  

### 2. Get methodology (no auth)

```bash
curl http://localhost:8000/v1/methodology
```

### 3. Assess a product (with API key)

```bash
curl -X POST http://localhost:8000/v1/assess-impact \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-api-key-change-in-production" \
  -d '{
    "product_name": "Organic Cotton T-Shirt",
    "material_composition": {"organic_cotton": 1.0},
    "weight_kg": 0.25,
    "origin_country": "India",
    "destination_country": "Germany"
  }'
```

---

## Authentication

| Header       | Required | Description        |
|-------------|----------|--------------------|
| `X-API-Key` | Yes (for `/v1/assess-impact`) | Your API key. Demo key: `demo-api-key-change-in-production`. |

`GET /v1/methodology` and `GET /health` do not require authentication.

---

## Endpoints

| Method | Endpoint            | Auth | Description |
|--------|---------------------|------|-------------|
| GET    | `/v1/methodology`   | No   | How we calculate scores and estimates. |
| POST   | `/v1/assess-impact` | Yes  | Assess a product; returns score, CO2, water, breakdown. |
| GET    | `/health`           | No   | Health check. |

---

## Request: Assess Impact

**POST `/v1/assess-impact`**

| Field                 | Type            | Required | Description |
|-----------------------|-----------------|----------|-------------|
| `product_name`        | string          | Yes      | Product name (e.g. "Organic Cotton T-Shirt"). |
| `material_composition`| object          | Yes      | Share per material, sum = 1.0. Example: `{"polyester": 0.6, "cotton": 0.4}`. |
| `weight_kg`           | number          | Yes      | Product weight in kg (> 0). |
| `origin_country`      | string          | Yes      | Production country (e.g. "CN", "Bangladesh"). |
| `destination_country` | string          | Yes      | Delivery country (e.g. "US", "Germany"). |

---

## Response: Assess Impact

Structured for AI agents and UIs:

| Field                      | Type   | Description |
|----------------------------|--------|-------------|
| `total_sustainability_score` | number | 0–100; higher = better. |
| `co2_estimate_kg`          | number | Estimated CO2 equivalent (kg). |
| `water_usage_liters`       | number | Estimated water usage (liters). |
| `breakdown`                | object | `material_score`, `logistics_score`, `weight_impact` (each 0–100). |
| `methodology_version`      | string | e.g. `"1.0.0-indicative"`. |

Example:

```json
{
  "total_sustainability_score": 68.5,
  "co2_estimate_kg": 4.2,
  "water_usage_liters": 1750.0,
  "breakdown": {
    "material_score": 72.0,
    "logistics_score": 65.0,
    "weight_impact": 90.0
  },
  "methodology_version": "1.0.0-indicative"
}
```

---

## Methodology

Results are **indicative estimates**, not a certified Life Cycle Assessment (LCA). Use **GET `/v1/methodology`** for full formulas, weights, and disclaimer. Summary:

- **Total score:** 50% materials + 30% logistics + 20% weight impact.
- **CO2:** Material emissions (per-kg factors) + distance-based logistics.
- **Water:** Material-based (e.g. cotton vs polyester).
- **Breakdown:** Separate scores for materials, logistics, and weight.

---

## Marketing & Sales

### Why this API is better for AI agents than generic carbon calculators

- **Structured, agent-ready output** — Responses are JSON with clear fields (`total_sustainability_score`, `co2_estimate_kg`, `water_usage_liters`, `breakdown`, `cbam_relevant`, `limitations`). Every field has a machine-readable description, so AI agents can interpret and cite results without scraping prose or PDFs.

- **Explainability and trust** — A dedicated **GET `/v1/methodology`** endpoint returns how scores and estimates are computed. Agents can surface this to users or use it to validate and explain numbers, which generic calculators rarely expose in a single, consistent API.

- **Product-level, not just company-level** — The API is built for **product** attributes (materials, weight, origin/destination). That fits e-commerce flows and Scope 3 product footprints, whereas many tools focus only on organization-level or facility-level carbon.

- **CBAM and regulatory signals** — The `cbam_relevant` flag highlights products that use steel, aluminum, or fertilizer, so agents can route users toward EU Carbon Border Adjustment Mechanism (CBAM) awareness. Generic calculators typically do not expose this as a first-class field.

- **Explicit limitations** — The `limitations` string states that estimates are model-based and for internal assessment, not final regulatory CBAM filings. That keeps agent-generated answers honest and reduces risk of overclaiming.

- **Rate limits and API key auth** — Designed for programmatic use: header-based API key and a simple rate limit (e.g. 5 req/s per key) make it safe to plug into agent loops and storefront backends without ad-hoc scraping or brittle UIs.

---

## RapidAPI / Listing

- **OpenAPI spec:** Generate `openapi.json` with:
  ```bash
  python export_openapi.py
  ```
- **RapidAPI-ready bundle** (tags + examples): Generate `rapidapi_ready.json` with:
  ```bash
  python generate_rapidapi_bundle.py
  ```
  This adds an `x-rapidapi-info` section with high-value tags (Sustainability, CBAM, Scope 3, AI Agent Tool, E-commerce) and an example for the assess-impact endpoint (Eco-friendly T-shirt, Recycled Cotton, 0.2 kg).
- Use `rapidapi_ready.json` (or `openapi.json`) to import the API into RapidAPI or any OpenAPI-based gateway.
- Ensure your listing mentions: API key in `X-API-Key` header; demo key for testing; indicative results, not certified LCA.

---

## Tech Stack

- **Python 3.12+**
- **FastAPI**
- **Pydantic v2** (schemas with descriptions)
- **API Key** (header: `X-API-Key`)

---

## Project Structure

```
.
├── main.py           # FastAPI app, routes
├── schemas.py        # Pydantic request/response models
├── logic.py          # Calculation engine (CO2, water, scores)
├── auth.py           # API key validation
├── export_openapi.py          # Dump openapi.json
├── generate_rapidapi_bundle.py # Build rapidapi_ready.json (tags + examples)
├── requirements.txt
├── openapi.json               # Generated spec
├── rapidapi_ready.json        # RapidAPI bundle (from script)
└── README.md
```

---

## License & Disclaimer

Results are for informational use only. Do not rely on them as the sole basis for compliance or marketing claims. Methodology may change; always check `methodology_version` and `/v1/methodology`.
