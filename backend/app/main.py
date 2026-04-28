import sys
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Load environment variables from the project root .env
# (CWD in Docker is /workspace/backend, but .env is at /workspace/.env)
load_dotenv(os.path.join(root_dir, ".env"))

# Setup Google credentials
key_path = os.path.join(root_dir, "gleaming-entry-471909-s1-5c03f3ad584a.json")
if os.path.exists(key_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

# Create app FIRST
app = FastAPI(title="CityScale API")

# Add CORS ONCE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes AFTER path setup
from app.api.routes import upload, analyze

app.include_router(upload.router, prefix="/upload")
app.include_router(analyze.router, prefix="/analyze")

@app.get("/")
def root():
    return {"message": "CityScale API running"}