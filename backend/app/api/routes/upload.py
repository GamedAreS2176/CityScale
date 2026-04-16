from fastapi import APIRouter, UploadFile, File
from app.services.gcs_service import upload_file

router = APIRouter()

@router.post("/")
async def upload_csv(file: UploadFile = File(...)):
    file_path = upload_file(file.file, file.filename)
    return {"file_path": file_path}