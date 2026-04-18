from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi import APIRouter
from app.api.routes import upload, analyze

app = FastAPI(title="CityScale API")
router=APIRouter()
app.include_router(upload.router, prefix="/upload")
app.include_router(analyze.router, prefix="/analyze")

@app.get("/")
def root():
    return {"message": "CityScale API running"}