def build_bias_prompt(summary):
    underfunded = summary.get("underfunded_regions", [])
    overfunded = summary.get("overfunded_regions", [])
    
    under_desc = ", ".join([f"{r['area']} ({round(r['bias_score']*100,1)}% deficit)" for r in underfunded])
    over_desc = ", ".join([f"{r['area']} ({round(r['bias_score']*100,1)}% excess)" for r in overfunded])
    
    prompt = f"""
You are an expert urban planner and data analyst. 
Analyze the following infrastructure funding allocation data:

Underfunded regions: {under_desc if underfunded else 'None'}
Overfunded regions: {over_desc if overfunded else 'None'}

Provide a short summary of the fairness implications and what the user should do next.
Do not start with "User wants", "We need to", or "Analysis:". Just provide the actionable insight.
"""
    return prompt.strip()