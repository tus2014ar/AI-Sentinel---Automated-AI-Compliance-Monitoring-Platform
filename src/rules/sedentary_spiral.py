import pandas as pd

def evaluate(df: pd.DataFrame) -> dict:
    # PROTOTYPE GUARDRAIL — not a legal threshold. Source: CMS §483.25(h) functional decline concern.
    
    result = {
        "rule_id": "R3_SEDENTARY_SPIRAL",
        "triggered": False,
        "severity": None,
        "metric_value": None,
        "threshold": None,
        "days_affected": 0,
        "regulation_reference": "CMS §483.25(h)",
        "regulation_url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.25",
        "threshold_justification": ">18 hours of sedentary time for multiple days strongly correlates with functional decline.",
        "confidence": "high",
        "data_quality_warning": None
    }
    
    # Null handling
    initial_len = len(df)
    # Only drop rows where the core metric is missing
    df_clean = df.dropna(subset=['sedentary_time']).copy()
    null_rows = initial_len - len(df_clean)
    if null_rows > 0:
        result["data_quality_warning"] = f"{null_rows} null rows skipped"
        
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)
    
    max_consecutive = 0
    current_consecutive = 0
    
    for val in df_clean['sedentary_time']:
        if val > 18.0:
            current_consecutive += 1
            if current_consecutive > max_consecutive:
                max_consecutive = current_consecutive
        else:
            current_consecutive = 0
            
    if max_consecutive >= 7:
        result["triggered"] = True
        result["severity"] = "High"
        result["metric_value"] = max_consecutive
        result["threshold"] = "7+ consecutive days"
        result["days_affected"] = max_consecutive
    elif max_consecutive >= 5:
        result["triggered"] = True
        result["severity"] = "Medium"
        result["metric_value"] = max_consecutive
        result["threshold"] = "5-6 consecutive days"
        result["days_affected"] = max_consecutive
        
    return result
