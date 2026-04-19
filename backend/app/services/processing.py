import pandas as pd
import numpy as np
from app.services.geo_mapper import add_coordinates

def process_csv(file_path: str):
    """
    Reads a CSV from a local path or GCS (gs://...) and returns analytical insights.
    Optimized to handle missing columns, bad data types, and missing fields.
    """
    try:
        # If file_path is gs://..., pandas will use gcsfs under the hood
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Failed to read CSV (Check if file exists and gcsfs is installed): {str(e)}"}

    # Strip whitespace and standardize column names
    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["region", "allocation", "population"]
    
    # Check if required columns exist
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        return {"error": f"Missing required columns: {missing}. Found: {df.columns.tolist()}"}

    # ==========================
    # DATA CLEANING & OPTIMIZATION
    # ==========================
    # 1. Drop rows where region is completely missing
    df = df.dropna(subset=['region'])
    
    # 2. Coerce numeric columns (e.g. "ERR" or "500k" becomes NaN) gracefully
    df["allocation"] = pd.to_numeric(df["allocation"], errors="coerce")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    
    # 3. Drop rows where we couldn't parse the numbers
    df = df.dropna(subset=["allocation", "population"])
    
    # 4. Avoid divide by zero error by replacing 0 population with NaN (which we drop)
    df["population"] = df["population"].replace(0, np.nan)
    df = df.dropna(subset=["population"])
    
    # ==========================
    # ANALYSIS
    # ==========================
    df["allocation_per_capita"] = df["allocation"] / df["population"]
    
    records = df.to_dict(orient="records")
    enriched_records = add_coordinates(records)

    # Calculate general summary statistics
    analysis = {
        "status": "success",
        "summary": {
            "total_allocation": float(df["allocation"].sum()),
            "total_population": float(df["population"].sum()),
            "average_allocation_per_capita": float(df["allocation_per_capita"].mean()),
            "valid_regions_processed": int(df["region"].nunique()),
            "data_cleaning": "Invalid, zero-population, or incomplete rows were ignored."
        },
        "records": enriched_records
    }

    return analysis
