from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.processing import process_csv
from ai_engine.pipelines.bias_pipeline import run_pipeline_from_dict

router = APIRouter()

class AnalyzeRequest(BaseModel):
    file_path: str

@router.post("/")
def analyze_data(request: AnalyzeRequest):

    # Step 1: Process CSV (add_coordinates already runs inside here)
    data = process_csv(request.file_path)

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    records = data.get("records", [])
    print(f"[DEBUG] Records from process_csv        : {len(records)}")

    # Step 2: Run bias pipeline
    try:
        bias_output = run_pipeline_from_dict(data, data)
        print(f"[DEBUG] bias_output type               : {type(bias_output)}")
    except Exception as e:
        print(f"[ERROR] Bias pipeline failed            : {e}")
        bias_output = None

    def _to_float(value):
        try:
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    def _normalize_point(item: dict):
        # Accept multiple possible key names from pipeline outputs
        lat = _to_float(item.get("lat"))
        if lat is None:
            lat = _to_float(item.get("latitude"))

        lng = _to_float(item.get("lng"))
        if lng is None:
            lng = _to_float(item.get("lon"))
        if lng is None:
            lng = _to_float(item.get("longitude"))

        bias_score = _to_float(item.get("bias_score"))
        if bias_score is None:
            bias_score = _to_float(item.get("bias"))
        if bias_score is None:
            bias_score = _to_float(item.get("score"))
        if bias_score is None:
            bias_score = _to_float(item.get("allocation_per_capita"))

        region = item.get("region") or item.get("name") or item.get("area") or "Unknown"

        allocation = item.get("allocation")
        population = item.get("population")
        allocation_per_capita = item.get("allocation_per_capita")

        if lat is None or lng is None or bias_score is None:
            return None
        if lat == 0.0 or lng == 0.0:
            return None

        return {
            "lat": lat,
            "lng": lng,
            "bias_score": bias_score,
            "region": region,
            "allocation": allocation,
            "population": population,
            "allocation_per_capita": allocation_per_capita,
        }

    # Step 3: Normalize output to [{lat, lng, bias_score, region, ...}]
    if isinstance(bias_output, list):
        normalized = []
        for item in bias_output:
            if isinstance(item, dict):
                point = _normalize_point(item)
                if point:
                    normalized.append(point)
        result = normalized

    else:
        # Pipeline failed or returned a dict — fall back to records from processing
        raw_result = [
            {
                "lat": row["lat"],
                "lng": row["lng"],
                "region": row.get("region", "Unknown"),
                "allocation": row.get("allocation"),
                "population": row.get("population"),
                "allocation_per_capita": row.get("allocation_per_capita"),
                "bias_score": row.get("allocation_per_capita", 0.0)
            }
            for row in records
            if row.get("lat", 0.0) != 0.0 and row.get("lng", 0.0) != 0.0
        ]

        # Normalize bias_score to [-1, +1] so radius stays reasonable on map
        scores = [r["bias_score"] for r in raw_result if r["bias_score"] is not None]
        max_score = max(scores) if scores else 1
        min_score = min(scores) if scores else 0
        mid = (max_score + min_score) / 2
        spread = (max_score - min_score) / 2 or 1

        for r in raw_result:
            r["bias_score"] = round((r["bias_score"] - mid) / spread, 4)

        result = raw_result

    print(f"[DEBUG] Final result sent to frontend   : {result}")
    return result