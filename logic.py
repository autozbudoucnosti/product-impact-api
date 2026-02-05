"""
Indicative calculation engine for product sustainability and impact (2026 model).
Uses 2026-aligned material factors, Great Circle Distance for logistics, and CBAM relevance.
"""

import math

# ---------------------------------------------------------------------------
# 2026 global average factors (kg CO2e per kg material)
# Recycled polyester ~30% lower than virgin; other values aligned to 2026 literature.
# ---------------------------------------------------------------------------
MATERIAL_CO2_KG_PER_KG: dict[str, float] = {
    "cotton": 5.2,
    "organic_cotton": 3.0,
    "polyester": 8.2,
    "recycled_polyester": 5.7,  # ~30% lower than virgin (8.2 * 0.70)
    "nylon": 8.8,
    "wool": 24.0,
    "linen": 1.9,
    "hemp": 2.3,
    "bamboo": 3.5,
    "viscose": 4.0,
    "lyocell": 2.6,
    "leather": 62.0,
    "rubber": 2.8,
    "steel": 1.85,
    "aluminum": 11.5,
    "cement": 0.85,
    "fertilizer": 2.1,
    "hydrogen": 10.0,
    "iron": 1.9,
    "default": 5.8,
}

# Indicative water usage (liters per kg material), 2026-oriented
MATERIAL_WATER_LITERS_PER_KG: dict[str, float] = {
    "cotton": 9_500,
    "organic_cotton": 6_500,
    "polyester": 95,
    "recycled_polyester": 70,
    "nylon": 95,
    "wool": 480,
    "linen": 1_900,
    "hemp": 2_400,
    "bamboo": 750,
    "viscose": 580,
    "lyocell": 380,
    "leather": 16_000,
    "rubber": 1_900,
    "steel": 150,
    "aluminum": 1_200,
    "cement": 50,
    "fertilizer": 200,
    "hydrogen": 20,
    "iron": 120,
    "default": 1_800,
}

# Normalized material sustainability (0–100): higher = lower impact
MATERIAL_SUSTAINABILITY_SCORE: dict[str, float] = {
    "cotton": 48,
    "organic_cotton": 74,
    "polyester": 36,
    "recycled_polyester": 72,  # better than virgin but not as extreme as old toy math
    "nylon": 34,
    "wool": 42,
    "linen": 76,
    "hemp": 82,
    "bamboo": 70,
    "viscose": 56,
    "lyocell": 72,
    "leather": 26,
    "rubber": 62,
    "steel": 55,
    "aluminum": 38,
    "cement": 50,
    "fertilizer": 52,
    "hydrogen": 45,
    "iron": 52,
    "default": 52,
}

# CBAM-relevant materials (EU Carbon Border Adjustment Mechanism)
CBAM_MATERIALS = frozenset({"steel", "aluminum", "cement", "fertilizer", "hydrogen", "iron"})
CBAM_MATERIALS_DISPLAY = "steel, aluminum, cement, fertilizer, hydrogen, or iron"

# Logistics: kg CO2e per kg product per 1000 km (2026 indicative, base = sea freight)
KG_CO2_PER_KG_PER_1000_KM = 0.58
MAX_DISTANCE_KM = 20_000
MIN_LOGISTICS_SCORE = 20
MAX_LOGISTICS_SCORE = 95

# Circuitry factors for real-world shipping routes (not straight lines)
MODE_CIRCUITRY_FACTOR: dict[str, float] = {
    "sea": 1.5,   # sea routes are ~50% longer than great circle
    "road": 1.2,  # road routes are ~20% longer
    "air": 1.0,   # air is close to great circle
    "rail": 1.0,  # rail is close to great circle
}

# CO2 multipliers by mode (relative to sea freight baseline)
MODE_CO2_MULTIPLIER: dict[str, float] = {
    "sea": 1.0,
    "road": 5.0,
    "rail": 2.0,
    "air": 50.0,  # air is ~50x more carbon intensive than sea
}

# Weight impact
WEIGHT_PENALTY_PER_KG = 2.0
WEIGHT_BASELINE_KG = 0.5

# Enterprise disclaimer
DISCLAIMER_TEXT = (
    "Indicative model-based estimate; not for regulatory CBAM filings."
)

# Earth radius (km) for Great Circle Distance
EARTH_RADIUS_KM = 6371.0

# Country name/code -> (lat, lon) approximate (capital or centroid). Expand as needed.
COUNTRY_COORDINATES: dict[str, tuple[float, float]] = {
    "at": (47.5162, 14.5501),
    "austria": (47.5162, 14.5501),
    "au": (-25.2744, 133.7751),
    "australia": (-25.2744, 133.7751),
    "be": (50.5039, 4.4699),
    "belgium": (50.5039, 4.4699),
    "bg": (42.7339, 25.4858),
    "bulgaria": (42.7339, 25.4858),
    "br": (-14.2350, -51.9253),
    "brazil": (-14.2350, -51.9253),
    "bd": (23.6850, 90.3563),
    "bangladesh": (23.6850, 90.3563),
    "ca": (56.1304, -106.3468),
    "canada": (56.1304, -106.3468),
    "cn": (35.8617, 104.1954),
    "china": (35.8617, 104.1954),
    "de": (51.1657, 10.4515),
    "germany": (51.1657, 10.4515),
    "fr": (46.2276, 2.2137),
    "france": (46.2276, 2.2137),
    "gb": (55.3781, -3.4360),
    "uk": (55.3781, -3.4360),
    "united kingdom": (55.3781, -3.4360),
    "in": (20.5937, 78.9629),
    "india": (20.5937, 78.9629),
    "it": (41.8719, 12.5674),
    "italy": (41.8719, 12.5674),
    "jp": (36.2048, 138.2529),
    "japan": (36.2048, 138.2529),
    "mx": (23.6345, -102.5528),
    "mexico": (23.6345, -102.5528),
    "nl": (52.1326, 5.2913),
    "netherlands": (52.1326, 5.2913),
    "pl": (51.9194, 19.1451),
    "poland": (51.9194, 19.1451),
    "pt": (39.3999, -8.2245),
    "portugal": (39.3999, -8.2245),
    "ro": (45.9432, 24.9668),
    "romania": (45.9432, 24.9668),
    "ru": (61.5240, 105.3188),
    "russia": (61.5240, 105.3188),
    "es": (40.4637, -3.7492),
    "spain": (40.4637, -3.7492),
    "tr": (38.9637, 35.2433),
    "turkey": (38.9637, 35.2433),
    "us": (37.0902, -95.7129),
    "usa": (37.0902, -95.7129),
    "united states": (37.0902, -95.7129),
    "vn": (14.0583, 108.2772),
    "vietnam": (14.0583, 108.2772),
}


def _normalize_material_key(key: str) -> str:
    """Normalize material name to our lookup key (lowercase, spaces to underscores)."""
    return key.strip().lower().replace(" ", "_")


def _normalize_country_key(key: str) -> str:
    """Normalize country for coordinate lookup."""
    return (key or "").strip().lower().replace(" ", "_")


def _get_material_value(mapping: dict[str, float], key: str) -> float:
    return mapping.get(key, mapping["default"])


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great circle distance in km between two (lat, lon) points."""
    lat1, lon1, lat2, lon2 = (
        math.radians(lat1),
        math.radians(lon1),
        math.radians(lat2),
        math.radians(lon2),
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def _distance_km(origin: str, destination: str) -> float:
    """Great Circle Distance between countries. Fallback for unknown countries."""
    o = _normalize_country_key(origin)
    d = _normalize_country_key(destination)
    if o == d or not o or not d:
        return 0.0
    coord_o = COUNTRY_COORDINATES.get(o)
    coord_d = COUNTRY_COORDINATES.get(d)
    if coord_o and coord_d:
        return _haversine_km(coord_o[0], coord_o[1], coord_d[0], coord_d[1])
    # Fallback: deterministic proxy so same pair always same distance
    h = hash((o, d)) % 10_000
    return 500.0 + float(h) % 14_500


def get_cbam_analysis(composition: dict[str, float]) -> dict:
    """
    CBAM relevance and reason for enterprise buyers.
    Checks for steel, aluminum, cement, fertilizer, hydrogen, iron.
    """
    found: list[str] = []
    for material in composition:
        if composition.get(material, 0) <= 0:
            continue
        key = _normalize_material_key(material)
        if key in CBAM_MATERIALS:
            found.append(material)
    is_relevant = len(found) > 0
    if is_relevant:
        reason = f"Product contains CBAM-relevant material(s): {', '.join(found)}."
    else:
        reason = f"Materials do not contain {CBAM_MATERIALS_DISPLAY}."
    return {"is_relevant": is_relevant, "reason": reason}


def compute_material_co2_kg(composition: dict[str, float], weight_kg: float) -> float:
    """CO2 from materials only (kg CO2e)."""
    total = 0.0
    for material, share in composition.items():
        if share <= 0:
            continue
        key = _normalize_material_key(material)
        co2_per_kg = _get_material_value(MATERIAL_CO2_KG_PER_KG, key)
        total += weight_kg * share * co2_per_kg
    return round(total, 2)


def compute_water_liters(composition: dict[str, float], weight_kg: float) -> float:
    """Water usage from materials (liters)."""
    total = 0.0
    for material, share in composition.items():
        if share <= 0:
            continue
        key = _normalize_material_key(material)
        water_per_kg = _get_material_value(MATERIAL_WATER_LITERS_PER_KG, key)
        total += weight_kg * share * water_per_kg
    return round(total, 2)


def compute_material_score(composition: dict[str, float]) -> float:
    """Weighted average material sustainability score (0–100)."""
    if not composition:
        return 50.0
    total_share = 0.0
    weighted = 0.0
    for material, share in composition.items():
        if share <= 0:
            continue
        key = _normalize_material_key(material)
        score = _get_material_value(MATERIAL_SUSTAINABILITY_SCORE, key)
        weighted += share * score
        total_share += share
    if total_share <= 0:
        return 50.0
    return round(weighted / total_share, 2)


def compute_logistics_co2_kg(
    origin_country: str,
    destination_country: str,
    weight_kg: float,
    mode: str = "sea",
) -> float:
    """
    Logistics CO2 (kg CO2e) from distance, weight, and shipping mode.
    Applies circuitry factor for real-world routes (sea: 1.5x, road: 1.2x).
    Applies CO2 multiplier by mode (air ~50x sea, road ~5x sea).
    """
    base_dist = _distance_km(origin_country, destination_country)
    mode_lower = mode.strip().lower()
    circuitry = MODE_CIRCUITRY_FACTOR.get(mode_lower, 1.0)
    co2_mult = MODE_CO2_MULTIPLIER.get(mode_lower, 1.0)
    effective_dist = min(base_dist * circuitry, MAX_DISTANCE_KM)
    co2 = weight_kg * (effective_dist / 1000.0) * KG_CO2_PER_KG_PER_1000_KM * co2_mult
    return round(co2, 2)


def compute_logistics_score(
    origin_country: str,
    destination_country: str,
    mode: str = "sea",
) -> float:
    """
    Logistics (shipping) sustainability score (0–100).
    Shorter distance = higher score. Mode affects score via CO2 multiplier penalty.
    """
    dist = _distance_km(origin_country, destination_country)
    if dist <= 0:
        return float(MAX_LOGISTICS_SCORE)
    mode_lower = mode.strip().lower()
    co2_mult = MODE_CO2_MULTIPLIER.get(mode_lower, 1.0)
    # Penalize high-CO2 modes
    mode_penalty = (co2_mult - 1.0) * 2.0  # e.g. air: (50-1)*2 = 98 penalty
    ratio = min(dist / 5000.0, 3.0)
    score = MAX_LOGISTICS_SCORE - (ratio * 25.0) - min(mode_penalty, 50.0)
    return round(max(MIN_LOGISTICS_SCORE, score), 2)


def compute_weight_impact_score(weight_kg: float) -> float:
    """Weight impact score (0–100). Lighter products score higher."""
    if weight_kg <= WEIGHT_BASELINE_KG:
        return 90.0
    penalty = (weight_kg - WEIGHT_BASELINE_KG) * WEIGHT_PENALTY_PER_KG
    score = 90.0 - penalty
    return round(max(10.0, min(90.0, score)), 2)


# ---------------------------------------------------------------------------
# Explainability engine
# ---------------------------------------------------------------------------

# Material-specific explanations
MATERIAL_EXPLANATIONS: dict[str, str] = {
    "polyester": "Polyester is a synthetic material with high energy intensity.",
    "nylon": "Nylon production is energy-intensive with significant CO2 emissions.",
    "cotton": "Conventional cotton has high water usage (up to 10,000 L/kg).",
    "organic_cotton": "Organic cotton uses less water and no synthetic pesticides.",
    "recycled_polyester": "Recycled polyester reduces virgin plastic use by ~30%.",
    "wool": "Wool production has high methane emissions from sheep.",
    "leather": "Leather has very high CO2 due to cattle farming and tanning.",
    "linen": "Linen (flax) is one of the most sustainable natural fibers.",
    "hemp": "Hemp requires minimal water and no pesticides; highly sustainable.",
    "bamboo": "Bamboo grows fast but processing can be chemical-intensive.",
    "steel": "Steel production is carbon-intensive (CBAM-relevant).",
    "aluminum": "Aluminum smelting is very energy-intensive (CBAM-relevant).",
    "cement": "Cement is a major industrial CO2 source (CBAM-relevant).",
    "iron": "Iron production involves high-temperature furnaces (CBAM-relevant).",
}


def generate_explanation(
    material_composition: dict[str, float],
    weight_kg: float,
    distance_km: float,
    mode: str,
) -> list[str]:
    """
    Generate human-readable explanations for the sustainability score.
    Returns a list of strings that AI agents can surface to users.
    """
    explanations: list[str] = []
    mode_lower = mode.strip().lower()

    # Material-specific explanations
    for material, share in material_composition.items():
        if share <= 0:
            continue
        key = _normalize_material_key(material)
        if key in MATERIAL_EXPLANATIONS:
            explanations.append(MATERIAL_EXPLANATIONS[key])

    # Mode-based explanations
    if mode_lower == "air":
        explanations.append(
            "Air freight penalty applied (approx 50x higher CO2 than sea freight)."
        )
    elif mode_lower == "road":
        explanations.append(
            "Road freight has ~5x higher CO2 than sea freight."
        )
    elif mode_lower == "sea":
        explanations.append(
            "Sea freight is the most carbon-efficient shipping mode."
        )
    elif mode_lower == "rail":
        explanations.append(
            "Rail freight is relatively efficient (~2x sea freight CO2)."
        )

    # Distance-based explanations
    if distance_km > 10_000:
        explanations.append(
            "Very long-distance shipping (>10,000 km) substantially increases emissions."
        )
    elif distance_km > 5_000:
        explanations.append(
            "Long-distance shipping significantly increases the score."
        )
    elif distance_km < 500 and distance_km > 0:
        explanations.append(
            "Short shipping distance (<500 km) keeps logistics impact low."
        )

    # Weight-based explanations
    if weight_kg > 5.0:
        explanations.append(
            f"Heavy product ({weight_kg:.1f} kg) adds significant weight penalty."
        )
    elif weight_kg < 0.3:
        explanations.append(
            "Lightweight product contributes to a better sustainability score."
        )

    return explanations


def assess_impact(
    product_name: str,
    material_composition: dict[str, float],
    weight_kg: float,
    origin_country: str,
    destination_country: str,
    shipping_mode: str = "sea",
) -> dict:
    """
    Full assessment with v1.2 indicative model.
    Returns dict including breakdown, CBAM analysis, and human-readable explanation.
    Weights: material 50%, logistics 30%, weight 20%.
    """
    mode = shipping_mode.strip().lower() if shipping_mode else "sea"

    material_score = compute_material_score(material_composition)
    logistics_score = compute_logistics_score(origin_country, destination_country, mode)
    weight_impact = compute_weight_impact_score(weight_kg)

    co2_materials = compute_material_co2_kg(material_composition, weight_kg)
    co2_logistics = compute_logistics_co2_kg(
        origin_country, destination_country, weight_kg, mode
    )
    co2_total = round(co2_materials + co2_logistics, 2)

    total_score = (
        0.50 * material_score + 0.30 * logistics_score + 0.20 * weight_impact
    )
    total_score = round(min(100.0, max(0.0, total_score)), 2)
    weight_penalty = round(100.0 - weight_impact, 2)

    # Compute distance for explanation
    distance_km = _distance_km(origin_country, destination_country)

    # Generate human-readable explanations
    explanation = generate_explanation(
        material_composition, weight_kg, distance_km, mode
    )

    return {
        "product_name": product_name,
        "total_sustainability_score": total_score,
        "confidence_level": "medium",
        "co2_estimate_kg": co2_total,
        "breakdown": {
            "material_score": material_score,
            "logistics_score": logistics_score,
            "weight_penalty": weight_penalty,
        },
        "cbam_analysis": get_cbam_analysis(material_composition),
        "explanation": explanation,
        "methodology_version": "v1.2.0",
        "disclaimer": DISCLAIMER_TEXT,
    }
