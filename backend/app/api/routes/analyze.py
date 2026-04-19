from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.processing import process_csv
from app.services.geo_mapper import add_coordinates

# Import the actual wrapper function
from ai_engine.pipelines.bias_pipeline import run_pipeline_from_dict

router = APIRouter()

class AnalyzeRequest(BaseModel):
    file_path: str

@router.post("/")
def analyze_data(request: AnalyzeRequest):
    """
    Provide the GCS file path or local file path to run analysis.
    """
    data = process_csv(request.file_path)
    
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
        
    data = add_coordinates(data.get("records", []))
    
    # In CityScale, pipeline currently expects two DFs: budget and census.
    # Because we're passing a single raw dict out of process_csv, we will
    # pass it identically to both args just to bypass the crash, or adapt:
    try:
        bias_output = run_pipeline_from_dict(data, data)
    except Exception as e:
        # Graceful fallback if data doesn't contain 'area', 'budget', etc. needed by bias_pipeline
        bias_output = {"info": "Pipeline error (Check data format)", "error": str(e), "data": data}

    return bias_output
