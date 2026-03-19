import pandas as pd
from . import mobility_suppression
from . import confinement_signal
from . import sedentary_spiral
from . import caregiver_overdependence
from . import alert_suppression_effect

def run_all_rules(resident_df: pd.DataFrame) -> list:
    """
    Runs all 5 deterministic AI Sentinel rules against a resident's pandas DataFrame.
    Returns a list of result dictionaries.
    """
    results = []
    
    results.append(mobility_suppression.evaluate(resident_df))
    results.append(confinement_signal.evaluate(resident_df))
    results.append(sedentary_spiral.evaluate(resident_df))
    results.append(caregiver_overdependence.evaluate(resident_df))
    results.append(alert_suppression_effect.evaluate(resident_df))
    
    return results
