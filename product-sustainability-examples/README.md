# Product Sustainability & CO2 Scoring Examples

This repository contains **copy-paste recipes** for integrating product sustainability and CO₂ scoring into your apps—whether you're building **e-commerce backends** (e.g. Shopify, WooCommerce) or **AI agents** (e.g. LangChain, custom chatbots). Use these examples as a starting point and adapt them to your stack.

---

## Getting Started

**You need a free API key to run these examples.**

Get your key here: **[https://rapidapi.com/autozbudoucnosti/api/sustainability-impact-assessment-api]**

Then either:

- Set the environment variable: `export RAPIDAPI_KEY=your_key_here`
- Or replace `YOUR_RAPIDAPI_KEY` in the example scripts with your key.

---

## What's in this repo

| File | Purpose |
|------|--------|
| **`shopify_product_score.py`** | Mock “fetch product from Shopify” → call the API → print a **Sustainability Report** for the product. |
| **`ai_agent_tool.py`** | Defines `get_product_carbon_footprint(product_name, material)` for LangChain or any AI agent; returns the **breakdown** text so the AI can explain it. |

---

## E-commerce: Shopify-style report

**`shopify_product_score.py`** demonstrates:

1. Simulating a product fetch from Shopify (replace with real Shopify Admin API when ready).
2. Calling the Product Sustainability API with the product name and inferred material.
3. Printing a formatted **Sustainability Report** (score, CO₂, breakdown) to the terminal.

**Run:**

```bash
pip install requests
export RAPIDAPI_KEY=your_key_here
python shopify_product_score.py
```

Adjust `API_BASE_URL` and the request payload in the script to match your actual API host and schema.

---

## AI agents: Carbon footprint tool

**`ai_agent_tool.py`** provides:

- **`get_product_carbon_footprint(product_name, material)`** — Calls the API and returns the **breakdown** text. Your AI can use this to answer questions like “What’s the carbon footprint of an organic cotton t-shirt?”

**Use as a plain function:**

```python
from ai_agent_tool import get_product_carbon_footprint

breakdown = get_product_carbon_footprint("Organic Cotton T-Shirt", material="cotton")
# Use `breakdown` in your agent's response
```

**Use as a LangChain tool (optional):**

```python
from ai_agent_tool import get_langchain_tool

tools = [get_langchain_tool()]
# Bind tools to your chain/agent
```

**Run standalone:**

```bash
pip install requests
export RAPIDAPI_KEY=your_key_here
python ai_agent_tool.py
```

---

## Requirements

- Python 3.8+
- `requests`
- For LangChain: `langchain-core` (only if you use `get_langchain_tool()`)

---

## License

Use these examples freely; adapt and integrate into your own projects. If you share improvements, a link back to this repo is appreciated.
