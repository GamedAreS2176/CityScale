from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def analyze_data():
    return {"message": "Analyze endpoint ready"}
