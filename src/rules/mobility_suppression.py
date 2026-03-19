import pandas as pd
import numpy as np

def evaluate(df: pd.DataFrame) -> dict:
    # PROTOTYPE GUARDRAIL — not a legal threshold. Source: CMS Appendix PP mobility decline concern.
    
    result = {
        "rule_id": "R1_MOBILITY_SUPPRESSION",
        "triggered": False,
        "severity": None,
        "metric_value": None,
        "threshold": None,
        "days_affected": [],
        "regulation_reference": "CMS §483.25(h)",
        "regulation_url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.25",
        "threshold_justification": "Steps dropping >30% or >40% after an alert indicates potential restraint-effect mobility suppression.",
        "confidence": "high",
        "data_quality_warning": None
    }
    
    # Null handling
    initial_len = len(df)
    
    # Fill NaN alert_triggered with False so we don't drop rows with otherwise good steps data
    df['alert_triggered'] = df['alert_triggered'].fillna(False)
    
    # Only drop rows where the core metric is missing
    df_clean = df.dropna(subset=['steps_per_day']).copy()
    null_rows = initial_len - len(df_clean)
    if null_rows > 0:
        result["data_quality_warning"] = f"{null_rows} null rows skipped"
        
    if len(df_clean) < 7:
        return result
        
    # Baseline Days 1-7
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)
    baseline_df = df_clean.head(7)
    baseline_steps = baseline_df['steps_per_day'].mean()
    
    if pd.isna(baseline_steps) or baseline_steps == 0:
        return result
        
    # Check for alerts
    alerts = df_clean[df_clean['alert_triggered'] == True]
    if alerts.empty:
        return result
        
    highest_severity = None
    worst_drop = 0.0
    worst_steps = baseline_steps
    days_affected = []
    
    for idx, alert_row in alerts.iterrows():
        # Check next 7 days after the alert
        post_alert = df_clean.iloc[idx+1:idx+8]
        if post_alert.empty:
            continue
            
        for _, row in post_alert.iterrows():
            steps = row['steps_per_day']
            drop_pct = (baseline_steps - steps) / baseline_steps
            
            if drop_pct > worst_drop:
                worst_drop = drop_pct
                worst_steps = steps
                
            if drop_pct > 0.40:
                highest_severity = "High"
                days_affected.append(row['date'])
            elif drop_pct > 0.30 and highest_severity != "High":
                highest_severity = "Medium"
                days_affected.append(row['date'])
                
    if highest_severity:
        result["triggered"] = True
        result["severity"] = highest_severity
        result["metric_value"] = round(worst_drop * 100, 1) # As a percentage drop
        result["threshold"] = "40% (High) or 30% (Medium)"
        result["days_affected"] = list(set(days_affected))
        
    return result
