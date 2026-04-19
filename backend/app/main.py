import sys
import os

# Important: Add the project root to sys.path so we can import top-level modules like ai_engine
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

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