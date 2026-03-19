# STATUS IS PRIMARY OUTPUT. Sub-scores are secondary visualization only and never override rule-based classification.

import pandas as pd
from typing import List
from src.models.analysis_result import AnalysisResult
from src.rules import run_all_rules

class AnalyzerEngine:
    
    def analyze_resident(self, resident_id: str, resident_df: pd.DataFrame) -> AnalysisResult:
        if resident_df.empty:
            return AnalysisResult(resident_id=resident_id, status="no_issue", confidence="low", ambiguous_cause=False)
            
        results = run_all_rules(resident_df)
        
        triggered_results = [r for r in results if r["triggered"]]
        high = [r for r in triggered_results if r["severity"] == "High"]
        medium = [r for r in triggered_results if r["severity"] == "Medium"]
        
        status = "no_issue"
        confidence = "high"
        ambiguous_cause = False
        
        # Helper to check if a specific rule triggered
        def is_triggered(rule_id):
            return any(r["rule_id"] == rule_id for r in triggered_results)
            
        def get_severity(rule_id):
            for r in triggered_results:
                if r["rule_id"] == rule_id:
                    return r["severity"]
            return None

        # Determine Classification
        if len(triggered_results) >= 2 or len(high) >= 1:
            status = "review_recommended"
            confidence = "high"
        elif len(medium) >= 1:
            status = "monitor"
            confidence = "medium"
        else:
            # Check for ambiguous mobility decline without alerts
            has_alerts = resident_df['alert_triggered'].any()
            # If no rules triggered but we see a significant decline in steps from the first 7 days vs last 7 days
            if len(resident_df) >= 14 and not has_alerts:
                df_sorted = resident_df.sort_values(by='date').reset_index(drop=True)
                base_steps = df_sorted.head(7)['steps_per_day'].mean()
                end_steps = df_sorted.tail(7)['steps_per_day'].mean()
                if base_steps > 0 and end_steps < (0.7 * base_steps):
                    status = "monitor"
                    confidence = "low"
                    ambiguous_cause = True
                else:
                    status = "no_issue"
                    confidence = "high"
            else:
                status = "no_issue"
                confidence = "high"
                
        # Sub-score computation
        mobility_score = 100.0
        r1_sev = get_severity("R1_MOBILITY_SUPPRESSION")
        if r1_sev == "High": mobility_score -= 40
        elif r1_sev == "Medium": mobility_score -= 20
        r3_sev = get_severity("R3_SEDENTARY_SPIRAL")
        if r3_sev == "High": mobility_score -= 20
        elif r3_sev == "Medium": mobility_score -= 10
        if get_severity("R5_ALERT_SUPPRESSION_EFFECT") == "High": mobility_score -= 30
        mobility_score = max(0.0, mobility_score)
        
        autonomy_score = 100.0
        r2_sev = get_severity("R2_CONFINEMENT_SIGNAL")
        if r2_sev == "High": autonomy_score -= 35
        elif r2_sev == "Medium": autonomy_score -= 20
        if is_triggered("R4_CAREGIVER_OVERDEPENDENCE"): autonomy_score -= 30
        if get_severity("R5_ALERT_SUPPRESSION_EFFECT") == "High": autonomy_score -= 15
        autonomy_score = max(0.0, autonomy_score)
        
        dignity_score = 100.0
        if is_triggered("R4_CAREGIVER_OVERDEPENDENCE"): dignity_score -= 40
        if r3_sev == "High": dignity_score -= 20
        elif r3_sev == "Medium": dignity_score -= 10
        if r2_sev == "High": dignity_score -= 15
        elif r2_sev == "Medium": dignity_score -= 10
        dignity_score = max(0.0, dignity_score)
        
        # Static regulatory mapping
        regulatory_notes = []
        if is_triggered("R1_MOBILITY_SUPPRESSION"):
            regulatory_notes.append("CMS guidance indicates monitoring interventions should not inhibit resident movement (42 CFR §483.25(h)).")
        if is_triggered("R2_CONFINEMENT_SIGNAL"):
            regulatory_notes.append("Residents have the right to freedom of movement. Spatial restriction warrants review under 42 CFR §483.10(e)(1).")
        if is_triggered("R3_SEDENTARY_SPIRAL"):
            regulatory_notes.append("Extended sedentary periods may indicate functional decline under CMS §483.25(h).")
        if is_triggered("R4_CAREGIVER_OVERDEPENDENCE"):
            regulatory_notes.append("Concurrent monitoring increase and mobility collapse may indicate over-assistance (42 CFR §483.12(a)(2)).")
        if is_triggered("R5_ALERT_SUPPRESSION_EFFECT"):
            regulatory_notes.append("Rapid behavioral change after alert introduction may indicate fear-of-movement per CMS Appendix PP.")
            
        regulatory_notes.append("This system supports compliance review and does not determine whether a regulatory violation has occurred.")
        
        return AnalysisResult(
            resident_id=resident_id,
            status=status,
            confidence=confidence,
            ambiguous_cause=ambiguous_cause,
            triggered_rules=[r["rule_id"] for r in triggered_results],
            triggered_rule_details=triggered_results,
            mobility_score=mobility_score,
            autonomy_score=autonomy_score,
            dignity_score=dignity_score,
            regulatory_notes=regulatory_notes
        )

    def analyze_dataset(self, filepath: str) -> List[AnalysisResult]:
        df = pd.read_csv(filepath)
        # Parse dates to string just to ensure consistency
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df['alert_triggered'] = df['alert_triggered'].apply(lambda x: True if str(x).lower() == 'true' else False)

        results = []
        for resident_id, group in df.groupby('resident_id'):
            res = self.analyze_resident(resident_id, group)
            results.append(res)
            
        return results
