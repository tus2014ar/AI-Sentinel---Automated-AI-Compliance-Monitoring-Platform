import pandas as pd

def evaluate(df: pd.DataFrame) -> dict:
    # PROTOTYPE GUARDRAIL — not a legal threshold. Source: NIST AI RMF Harm Assessment — rapid behavioral change following system intervention.
    
    result = {
        "rule_id": "R5_ALERT_SUPPRESSION_EFFECT",
        "triggered": False,
        "severity": None,
        "metric_value": None,
        "threshold": None,
        "days_affected": [],
        "regulation_reference": "NIST AI RMF",
        "regulation_url": "https://airc.nist.gov/RMF",
        "threshold_justification": "Rapid movement drop >40% after a *new* alert indicates harmful system intervention effect.",
        "confidence": "high",
        "data_quality_warning": None
    }
    
    # Null handling
    initial_len = len(df)
    
    df['alert_triggered'] = df['alert_triggered'].fillna(False)
    
    # Don't dropna on alert_type, as it is expected to be NaN/null on days without alerts.
    df_clean = df.dropna(subset=['movement_events_per_day']).copy()
    null_rows = initial_len - len(df_clean)
    if null_rows > 0:
        result["data_quality_warning"] = f"{null_rows} null rows skipped"
        
    if len(df_clean) < 3:
        return result
        
    df_clean = df_clean.sort_values(by='date').reset_index(drop=True)
    
    seen_alert_types = set()
    
    for idx, row in df_clean.iterrows():
        if row['alert_triggered']:
            a_type = row['alert_type']
            
            # Find NEW alert type
            if a_type not in seen_alert_types:
                seen_alert_types.add(a_type)
                
                # Compare 2 days before vs 2 days after (if enough data exists)
                if idx >= 2 and idx + 2 < len(df_clean):
                    before_window = df_clean.iloc[idx-2:idx]
                    after_window = df_clean.iloc[idx+1:idx+3]
                    
                    base_movement = before_window['movement_events_per_day'].mean()
                    post_movement = after_window['movement_events_per_day'].mean()
                    
                    if pd.isna(base_movement) or base_movement == 0:
                        continue
                        
                    drop_pct = (base_movement - post_movement) / base_movement
                    
                    if drop_pct > 0.40:
                        result["triggered"] = True
                        result["severity"] = "High"
                        result["metric_value"] = round(drop_pct * 100, 1)
                        result["threshold"] = "40% drop over 48h window"
                        result["days_affected"] = after_window['date'].tolist()
                        return result # Return on first instance
                        
    return result
