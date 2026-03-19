import pandas as pd

def evaluate(df: pd.DataFrame) -> dict:
    # PROTOTYPE GUARDRAIL — not a legal threshold. Source: CMS §483.12(a)(2) learned helplessness and over-assistance concern.
    
    result = {
        "rule_id": "R4_CAREGIVER_OVERDEPENDENCE",
        "triggered": False,
        "severity": None,
        "metric_value": None,
        "threshold": None,
        "days_affected": [],
        "regulation_reference": "CMS §483.12(a)(2)",
        "regulation_url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.12",
        "threshold_justification": "Caregiver time doubling while steps halve indicates potential learned helplessness.",
        "confidence": "high",
        "data_quality_warning": None
    }
    
    # Null handling
    initial_len = len(df)
    
    # Only drop rows where the core metrics are missing
    df_clean = df.dropna(subset=['caregiver_time_with_resident', 'steps_per_day']).copy()
    null_rows = initial_len - len(df_clean)
    if null_rows > 0:
        result["data_quality_warning"] = f"{null_rows} null rows skipped"
        
    if len(df_clean) < 14:
        return result
        
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)
    
    # Sliding 14-day window
    for i in range(len(df_clean) - 13):
        window = df_clean.iloc[i:i+14]
        
        baseline = window.iloc[0:7]
        current_period = window.iloc[7:14]
        
        base_care = baseline['caregiver_time_with_resident'].mean()
        base_steps = baseline['steps_per_day'].mean()
        
        if pd.isna(base_care) or pd.isna(base_steps) or base_care == 0 or base_steps == 0:
            continue
            
        curr_care = current_period['caregiver_time_with_resident'].mean()
        curr_steps = current_period['steps_per_day'].mean()
        
        if (curr_care >= 2 * base_care) and (curr_steps <= 0.5 * base_steps):
            result["triggered"] = True
            result["severity"] = "High"
            result["metric_value"] = f"Care: {curr_care:.1f} (base {base_care:.1f}), Steps: {curr_steps:.1f} (base {base_steps:.1f})"
            result["threshold"] = "Care >= 2x AND Steps <= 0.5x"
            result["days_affected"] = current_period['date'].tolist()
            return result # Return on first trigger found for MVP simplicity
            
    return result
