from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.processing import process_csv

router = APIRouter()

class AnalyzeRequest(BaseModel):
    file_path: str

@router.post("/")
def analyze_data(request: AnalyzeRequest):
    """
    Provide the GCS file path or local file path to run analysis.
    """
    analysis_result = process_csv(request.file_path)
    
    if "error" in analysis_result:
        raise HTTPException(status_code=400, detail=analysis_result["error"])
        
    return analysis_result
