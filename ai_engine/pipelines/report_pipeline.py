import sys
from pathlib import Path

# Add project root to path when running this file directly
# TEMP: Local import fix for standalone testing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_engine.llm.prompt_templates import build_bias_prompt
from ai_engine.llm.gemini_client import generate_report


# -------------------------
# Structured fallback report
# -------------------------
def generate_structured_report(summary):
    underfunded = summary.get("underfunded_regions", [])
    overfunded = summary.get("overfunded_regions", [])

    if not underfunded and not overfunded:
        return "No significant allocation bias detected across regions."

    # Extract names + percentages
    under_desc = ", ".join(
        [f"{r['area']} ({round(r['bias_score']*100,1)}% deficit)" for r in underfunded]
    ) if underfunded else "none"

    over_desc = ", ".join(
        [f"{r['area']} ({round(r['bias_score']*100,1)}% excess)" for r in overfunded]
    ) if overfunded else "none"

    return f"""
Key Finding:
Underfunded regions: {under_desc}.

Why This Is Unfair:
These regions receive significantly less funding than expected, while {over_desc} receive disproportionately higher allocation. This creates unequal infrastructure access.

Recommendation:
Reallocate funds from overfunded regions ({over_desc}) to underfunded regions ({under_desc}) based on proportional population and vulnerability needs.
"""
# -------------------------
# Clean LLM output
# -------------------------
def clean_llm_output(text):
    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line_lower = line.lower()

        if "user wants" in line_lower:
            continue
        if "we need to" in line_lower:
            continue
        if "analysis:" in line_lower:
            continue

        clean_lines.append(line.strip())

    return "\n".join(clean_lines).strip()


# -------------------------
# Main report pipeline
# -------------------------
def run_report_pipeline(summary):

    # FIX: Ensure correct keys exist
    underfunded = summary.get("underfunded_regions", [])
    overfunded = summary.get("overfunded_regions", [])

    # Always generate base report first (source of truth)
    base_report = generate_structured_report(summary)

    # If no bias → do NOT call LLM at all
    if not underfunded and not overfunded:
        return base_report

    try:
        prompt = build_bias_prompt(summary)
        llm_report = generate_report(prompt)

        # Clean LLM output
        llm_report = clean_llm_output(llm_report)

        # Strong validation
        if (
            len(llm_report) < 40
            or "user wants" in llm_report.lower()
            or "no significant" in llm_report.lower()
        ):
            return base_report

        return base_report + "\n\nAdditional Insight:\n" + llm_report

    except Exception as e:
        return base_report


# -------------------------
# Standalone test
# -------------------------
if __name__ == "__main__":
    test_summary = {
        "total_regions": 4,
        "underfunded_regions": [{"area": "Ward-2", "bias_score": -0.3}],
        "overfunded_regions": [{"area": "Ward-5", "bias_score": 0.4}],
        "avg_bias": 0.2
    }

    print("Running standalone test...")
    output = run_report_pipeline(test_summary)
    print("Final Output:\n", output)