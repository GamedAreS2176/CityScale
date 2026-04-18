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

    # Load data
    budget_df = pd.read_csv(budget_path)
    census_df = pd.read_csv(census_path)

    df = budget_df.merge(census_df, on="area")

    if df.empty:
        raise ValueError("Merged dataset is empty. Check input data.")

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