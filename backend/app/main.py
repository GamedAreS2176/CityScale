from fastapi import FastAPI
from app.api.routes import upload, analyze

app = FastAPI(title="CityScale API")

app.include_router(upload.router, prefix="/upload")
app.include_router(analyze.router, prefix="/analyze")

@app.get("/")
def root():
    return {"message": "CityScale API running"}