"""
Export OpenAPI schema to openapi.json for RapidAPI or static hosting.
Run: python export_openapi.py
"""

import json
from main import app

if __name__ == "__main__":
    schema = app.openapi()
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print("Written openapi.json")
