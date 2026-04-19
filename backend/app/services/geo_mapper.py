import json
import os

# Resolve the absolute path to the data folder from the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
mapping_path = os.path.join(project_root, "data", "mappings", "region_latlng.json")

try:
    with open(mapping_path) as f:
        REGION_MAP = json.load(f)
except FileNotFoundError:
    REGION_MAP = {}

def add_coordinates(data):
    for row in data:
        region = row.get("region", "")
        coords = REGION_MAP.get(region, {"lat": 0.0, "lng": 0.0})
        row["lat"] = coords["lat"]
        row["lng"] = coords["lng"]
    return data