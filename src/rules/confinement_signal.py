import pandas as pd

def evaluate(df: pd.DataFrame) -> dict:
    # PROTOTYPE GUARDRAIL — not a legal threshold. Source: CMS §483.10(e)(1) autonomy and freedom of movement.
    
    result = {
        "rule_id": "R2_CONFINEMENT_SIGNAL",
        "triggered": False,
        "severity": None,
        "metric_value": None,
        "threshold": None,
        "days_affected": 0,
        "regulation_reference": "CMS §483.10(e)(1)",
        "regulation_url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.10",
        "threshold_justification": "Visiting <2 rooms for multiple consecutive days indicates potential confinement.",
        "confidence": "high",
        "data_quality_warning": None
    }
    
    # Null handling
    initial_len = len(df)
    # Only drop rows where the core metric is missing
    df_clean = df.dropna(subset=['rooms_visited_per_day']).copy()
    null_rows = initial_len - len(df_clean)
    if null_rows > 0:
        result["data_quality_warning"] = f"{null_rows} null rows skipped"
        
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)
    
    max_consecutive = 0
    current_consecutive = 0
    
    for val in df_clean['rooms_visited_per_day']:
        if val < 2:
            current_consecutive += 1
            if current_consecutive > max_consecutive:
                max_consecutive = current_consecutive
        else:
            current_consecutive = 0
            
    if max_consecutive >= 5:
        result["triggered"] = True
        result["severity"] = "High"
        result["metric_value"] = max_consecutive
        result["threshold"] = "5+ consecutive days"
        result["days_affected"] = max_consecutive
    elif max_consecutive >= 3:
        result["triggered"] = True
        result["severity"] = "Medium"
        result["metric_value"] = max_consecutive
        result["threshold"] = "3-4 consecutive days"
        result["days_affected"] = max_consecutive
        
    return result
