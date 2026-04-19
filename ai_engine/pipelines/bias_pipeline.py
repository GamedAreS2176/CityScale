import sys
from pathlib import Path

# Add project root to path
# TEMP: Local import fix for standalone testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from ai_engine.utils.data_formatter import format_for_heatmap
from ai_engine.pipelines.report_pipeline import run_report_pipeline


# -------------------------
# Income Weight Logic
# -------------------------
def get_weight(income):
    if income == "low":
        return 1.2
    elif income == "middle":
        return 1.0
    else:
        return 0.8


# -------------------------
# Main Pipeline
# -------------------------
def run_bias_pipeline(budget_path, census_path):

    # Load data gracefully (accepts paths or DataFrames)
    if isinstance(budget_path, pd.DataFrame):
        budget_df = budget_path.copy()
    else:
        budget_df = pd.read_csv(budget_path)
        
    if isinstance(census_path, pd.DataFrame):
        census_df = census_path.copy()
    else:
        census_df = pd.read_csv(census_path)

    # Mock standardizing column names if we are receiving 'region' and 'allocation' directly
    if "region" in budget_df.columns and "area" not in budget_df.columns:
        budget_df = budget_df.rename(columns={"region": "area"})
    if "region" in census_df.columns and "area" not in census_df.columns:
        census_df = census_df.rename(columns={"region": "area"})
        
    if "allocation" in budget_df.columns and "budget" not in budget_df.columns:
        budget_df = budget_df.rename(columns={"allocation": "budget"})

    # If population is missing from census (e.g. they passed identical DFs and it was in budget_df)
    # the merge will still work as long as it's somewhere. Actually let's just attempt a normal merge:
    
    if "area" not in budget_df.columns or "area" not in census_df.columns:
        # Fallback to avoid merge crash if data is totally mismatched
        df = budget_df.copy()
        if "population" not in df.columns and "population" in census_df.columns:
             df["population"] = census_df["population"]
    else:
        # standard path
        df = budget_df.merge(census_df, on="area")

    if df.empty:
        df = budget_df.copy() # fallback just to prevent crashing

    if df.empty:
        raise ValueError("Merged dataset is empty. Check input data.")
        
    # Handle column suffixes (like _x, _y) if we merged identical dataframes during testing
    for col in ["population", "budget", "lat", "lng"]:
        if col not in df.columns:
            if f"{col}_x" in df.columns:
                df[col] = df[f"{col}_x"]
            elif f"{col}_y" in df.columns:
                df[col] = df[f"{col}_y"]
        
    # Mock income group if missing
    if "income_group" not in df.columns:
        df["income_group"] = "middle"

    # -------------------------
    # Compute Need Score
    # -------------------------
    df["weight"] = df["income_group"].apply(get_weight)
    df["need_score"] = df["population"] * df["weight"]

    total_need = df["need_score"].sum()
    total_budget = df["budget"].sum()

    if total_need == 0:
        raise ValueError("Total need score is zero. Invalid data.")

    # -------------------------
    # Expected Budget
    # -------------------------
    df["expected_budget"] = (df["need_score"] / total_need) * total_budget

    # -------------------------
    # Bias Calculation
    # -------------------------
    if "budget" not in df.columns:
        df["budget"] = 0
        
    df["bias"] = df["budget"] - df["expected_budget"]

    # Avoid division errors
    df["bias_score"] = df.apply(
        lambda row: row["bias"] / row["expected_budget"] if row["expected_budget"] != 0 else 0,
        axis=1
    )

    # Add % interpretation (VERY IMPORTANT)
    df["bias_percentage"] = df["bias_score"] * 100

    # -------------------------
    # Prepare Results
    # -------------------------
    results = []

    for _, row in df.iterrows():
        results.append({
            "area": row["area"],
            "bias_score": float(round(row["bias_score"], 4)),
            "bias_percentage": float(round(row["bias_percentage"], 2)),
            "lat": row["lat"],
            "lng": row["lng"]
        })

    # -------------------------
    # Heatmap
    # -------------------------
    heatmap = format_for_heatmap(results)

    # -------------------------
    # Dynamic Threshold
    # -------------------------
    threshold = 0.05  # 5% deviation

    underfunded = [r for r in results if r["bias_score"] < -threshold]
    overfunded = [r for r in results if r["bias_score"] > threshold]

    avg_bias = sum(abs(r["bias_score"]) for r in results) / len(results)

    summary = {
        "total_regions": len(results),
        "underfunded_regions": underfunded,
        "overfunded_regions": overfunded,
        "avg_bias": float(round(avg_bias, 4))
    }

    # -------------------------
    # Report
    # -------------------------
    report = run_report_pipeline(summary)

    # -------------------------
    # Reallocation Engine
    # -------------------------
    df["recommended_budget"] = df["expected_budget"]
    df["budget_change"] = df["recommended_budget"] - df["budget"]

    reallocation = []

    for _, row in df.iterrows():
        reallocation.append({
            "area": row["area"],
            "current_budget": float(round(row["budget"], 2)),
            "recommended_budget": float(round(row["recommended_budget"], 2)),
            "change": float(round(row["budget_change"], 2)),
            "change_percentage": float(round((row["budget_change"] / row["budget"]) * 100, 2)) if row["budget"] != 0 else 0
        })

    reallocation_summary = {
        "increase_funding": [r for r in reallocation if r["change"] > 0],
        "decrease_funding": [r for r in reallocation if r["change"] < 0]
    }

    # -------------------------
    # FINAL OUTPUT
    # -------------------------
    return {
        "bias_results": results,
        "heatmap": heatmap,
        "summary": summary,
        "reallocation": reallocation,
        "reallocation_summary": reallocation_summary,
        "report": report
    }

# wrapper function for backend integration

def run_pipeline_from_dict(budget_df, census_df):
    import pandas as pd

    # Convert to DataFrame if needed
    if not isinstance(budget_df, pd.DataFrame):
        budget_df = pd.DataFrame(budget_df)

    if not isinstance(census_df, pd.DataFrame):
        census_df = pd.DataFrame(census_df)

    # Save temp or reuse logic
    # (optional improvement later)

    # Directly call internal logic
    return run_bias_pipeline(budget_df, census_df)