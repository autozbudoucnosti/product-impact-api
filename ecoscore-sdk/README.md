# ecoscore-sdk

Python client for the **Product Sustainability & Impact Assessment API**. Get sustainability scores, CO2 estimates, and water usage for products in a few lines of code—ideal for e-commerce, dashboards, and AI agents.

**Get your free API key:** [RapidAPI – Product Sustainability & Impact Assessment API](https://rapidapi.com/hub) *(replace with your actual RapidAPI API page URL once listed)*

---

## Install

```bash
pip install ecoscore-sdk
```

---

## Quick start

```python
from ecoscore import EcoClient

client = EcoClient(
    api_key="YOUR_API_KEY",           # from RapidAPI
    base_url="https://yourapp.railway.app",  # your API base URL
)
impact = client.assess_impact(product="T-Shirt", material="Cotton")
print(impact.co2_estimate)              # e.g. 1.15
print(impact.total_sustainability_score)
print(impact.water_usage_liters)
```

Or use environment variables:

```bash
export ECOSCORE_API_KEY=your_key
export ECOSCORE_BASE_URL=https://yourapp.railway.app
```

```python
from ecoscore import EcoClient

client = EcoClient()
impact = client.assess_impact(product="Eco T-Shirt", material="Organic Cotton", weight_kg=0.2)
print(impact.co2_estimate)
print(impact.cbam_relevant)
print(impact.limitations)
```

---

## API

### `EcoClient(api_key=None, base_url=None)`

- **api_key:** Your API key (from [RapidAPI](https://rapidapi.com) or your provider). Can be omitted if `ECOSCORE_API_KEY` is set.
- **base_url:** API root URL (e.g. `https://yourapp.railway.app`). Can be omitted if `ECOSCORE_BASE_URL` is set.

### `assess_impact(product, material, weight_kg=0.2, origin_country="CN", destination_country="US")`

- **product:** Product name (string).
- **material:** Single material name (e.g. `"Cotton"`, `"Recycled Polyester"`) or a dict of shares, e.g. `{"cotton": 0.6, "polyester": 0.4}`.
- **weight_kg:** Weight in kilograms (default `0.2`).
- **origin_country:** Production country (default `"CN"`).
- **destination_country:** Delivery country (default `"US"`).

Returns an **`ImpactResult`** with:

- `co2_estimate` / `co2_estimate_kg` — CO2 equivalent (kg)
- `water_usage_liters` — Water use (liters)
- `total_sustainability_score` — 0–100 score
- `breakdown` — `material_score`, `logistics_score`, `weight_impact`
- `cbam_relevant` — Whether the product contains CBAM-relevant materials
- `limitations` — Disclaimer text (internal use, not for regulatory filings)

### `get_methodology()`

Returns the calculation methodology (formulas, weights, disclaimer) as a dict.

---

## Where to get the API key

This SDK talks to the **Product Sustainability & Impact Assessment API**. To use it:

1. Go to **RapidAPI** and find the **Product Sustainability & Impact Assessment API** (or use the link on the API’s GitHub repo). Subscribe to the free tier and copy your API key.
2. Copy your **API key** and your **base URL** (if provided).
3. Pass them into `EcoClient(api_key="...", base_url="...")` or set `ECOSCORE_API_KEY` and `ECOSCORE_BASE_URL`.

---

## License

MIT.
