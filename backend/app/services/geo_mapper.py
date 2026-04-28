import json
import os
import time
from typing import Dict, Tuple, Optional

import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
mapping_path = os.path.join(project_root, "data", "mappings", "region_latlng.json")

try:
    with open(mapping_path) as f:
        raw_map = json.load(f)
except FileNotFoundError:
    raw_map = {}
    print("[WARNING] region_latlng.json not found at:", mapping_path)

# Build a normalized lookup: {"downtown": {...}, "uptown": {...}, ...}
# This means CSV values like "Downtown", "DOWNTOWN", " downtown " all match
REGION_MAP = {k.strip().lower(): v for k, v in raw_map.items()}

_GEOCODE_CACHE: Dict[str, Dict[str, float]] = {}
_LAST_NOMINATIM_CALL_TS = 0.0


def _ensure_mapping_dir():
    mapping_dir = os.path.dirname(mapping_path)
    os.makedirs(mapping_dir, exist_ok=True)


def _persist_mapping():
    try:
        _ensure_mapping_dir()
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(REGION_MAP, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[WARNING] Failed to persist region map:", e)


def _nominatim_geocode(query: str) -> Optional[Tuple[float, float]]:
    """
    Lightweight fallback geocoder (OpenStreetMap Nominatim).
    Best-effort only; rate-limited and cached in-memory.
    """
    global _LAST_NOMINATIM_CALL_TS

    q = query.strip()
    if not q:
        return None

    # Rate-limit: Nominatim expects ~1 req/sec for heavy usage
    now = time.time()
    wait_s = 1.05 - (now - _LAST_NOMINATIM_CALL_TS)
    if wait_s > 0:
        time.sleep(wait_s)

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": "CityScale/1.0 (hackathon demo)"},
            timeout=12,
        )
        _LAST_NOMINATIM_CALL_TS = time.time()
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        lat = float(results[0]["lat"])
        lng = float(results[0]["lon"])
        return lat, lng
    except Exception as e:
        print(f"[WARNING] Geocoding failed for '{q}': {e}")
        return None


def add_coordinates(data):
    unmatched = []

    for row in data:
        region_raw = row.get("region", "")
        region_key = str(region_raw).strip().lower()   # normalize before lookup

        coords = REGION_MAP.get(region_key) or _GEOCODE_CACHE.get(region_key)

        if coords:
            row["lat"] = coords["lat"]
            row["lng"] = coords["lng"]
        else:
            # Fallback: try geocoding if not in static mapping.
            # Default to India context if user provided short region names.
            query = str(region_raw).strip()
            if query and "," not in query:
                query = f"{query}, India"

            resolved = _nominatim_geocode(query) if query else None
            if resolved:
                lat, lng = resolved
                row["lat"] = lat
                row["lng"] = lng
                REGION_MAP[region_key] = {"lat": lat, "lng": lng}
                _GEOCODE_CACHE[region_key] = {"lat": lat, "lng": lng}
                _persist_mapping()
            else:
                row["lat"] = 0.0
                row["lng"] = 0.0
                unmatched.append(region_raw)

    if unmatched:
        print(f"[WARNING] Regions not found in map: {list(set(unmatched))}")
        print(f"[DEBUG]   Available keys in map   : {list(REGION_MAP.keys())}")

    return data