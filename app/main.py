import streamlit as st
import pandas as pd
import os
import sys

# Ensure correct imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.engine.analyzer import AnalyzerEngine
from src.ai_explainer.explainer import LocalAIExplainer
from src.audit_logger import AuditLogger

st.set_page_config(page_title="AI Sentinel for MyRaina", layout="wide")

@st.cache_resource
def get_engine():
    return AnalyzerEngine()

@st.cache_resource
def get_explainer():
    return LocalAIExplainer()
    
@st.cache_resource
def get_logger():
    return AuditLogger()

engine = get_engine()
explainer = get_explainer()
logger = get_logger()

# State initialization
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

def run_analysis(uploaded_file):
    temp_path = os.path.join(parent_dir, 'data', 'temp_upload.csv')
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.session_state.filename = uploaded_file.name
    results = engine.analyze_dataset(temp_path)
    
    all_res = []
    for r in results:
        exp = explainer.generate_explanation(r)
        all_res.append({
            "resident_id": r.resident_id,
            "status": r.status,
            "confidence": r.confidence,
            "ambiguous_cause": r.ambiguous_cause,
            "triggered_rules": r.triggered_rules,
            "triggered_rule_details": r.triggered_rule_details,
            "mobility_score": r.mobility_score,
            "autonomy_score": r.autonomy_score,
            "dignity_score": r.dignity_score,
            "regulatory_notes": r.regulatory_notes,
            "explanation": exp['explanation'],
            "workflow_insights": exp['workflow_insights'],
            "disclaimer": exp['disclaimer']
        })
        
    st.session_state.analysis_results = all_res
    st.session_state.df = pd.DataFrame(all_res)
    
    # Audit log
    review_rec = sum(1 for r in all_res if r['status'] == 'review_recommended')
    monitor = sum(1 for r in all_res if r['status'] == 'monitor')
    no_issue = sum(1 for r in all_res if r['status'] == 'no_issue')
    logger.log_run(uploaded_file.name, len(all_res), review_rec, monitor, no_issue)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

st.title("AI Sentinel for MyRaina")
st.markdown("##### *Analyzes resident mobility patterns to support CMS least-restrictive care compliance review.*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Findings", "Residents", "Audit Log", "System Transparency"
])

def get_color(status):
    if status == 'no_issue': return "green"
    if status == 'monitor': return "orange"
    return "red"

with tab1:
    uploaded_file = st.file_uploader("Upload Resident Data CSV", type="csv")
    if uploaded_file is not None and st.session_state.filename != uploaded_file.name:
        with st.spinner("Analyzing data..."):
            run_analysis(uploaded_file)
            
    if st.session_state.analysis_results is not None:
        df_res = st.session_state.df
        
        no_issue_count = len(df_res[df_res['status'] == 'no_issue'])
        monitor_count = len(df_res[df_res['status'] == 'monitor'])
        review_count = len(df_res[df_res['status'] == 'review_recommended'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ No Issue", no_issue_count)
        col2.metric("⚠️ Monitor", monitor_count)
        col3.metric("🔴 Review Recommended", review_count)
        
        st.markdown("### Summary Table")
        
        def color_status(val):
            return f'color: {get_color(val)}; font-weight: bold'
            
        display_df = df_res[['resident_id', 'status', 'confidence', 'mobility_score', 'autonomy_score']].copy()
        st.dataframe(display_df.style.map(color_status, subset=['status']), use_container_width=True)
        
    st.markdown("---")
    if st.button("Run on Real Data"):
        st.info("Connect a live MyRaina data feed to analyze current resident activity.")

with tab2:
    st.subheader("Resident Findings")
    if st.session_state.analysis_results is not None:
        res_list = [r['resident_id'] for r in st.session_state.analysis_results]
        selected_res = st.selectbox("Select Resident", res_list)
        
        if selected_res:
            data = next(r for r in st.session_state.analysis_results if r['resident_id'] == selected_res)
            
            st.markdown(f"### Status: <span style='color:{get_color(data['status'])};'>{data['status'].upper()}</span> (Confidence: {data['confidence']})", unsafe_allow_html=True)
            
            if data['ambiguous_cause']:
                st.warning("⚠️ Mobility decline detected without alert event. Cause may be health-related. Clinical review recommended before escalation.")
                
            st.markdown("#### Triggered Rules")
            if not data['triggered_rule_details']:
                st.success("No behavioral indicators triggered.")
            else:
                for rule in data['triggered_rule_details']:
                    with st.expander(f"Rule: {rule['rule_id']}"):
                        st.markdown(f"**Metric Value:** {rule['metric_value']}")
                        st.markdown(f"**Threshold:** {rule['threshold']}")
                        st.markdown(f"**Regulation:** [{rule['regulation_reference']}]({rule['regulation_url']})")
                        st.markdown(f"**Justification:** {rule['threshold_justification']}")
                        if rule.get('data_quality_warning'):
                            st.warning(f"Data Quality Warning: {rule['data_quality_warning']}")

            st.markdown("#### Secondary Indicators (Sub-scores)")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Mobility Score", f"{data['mobility_score']:.0f}/100")
            sc2.metric("Autonomy Score", f"{data['autonomy_score']:.0f}/100")
            sc3.metric("Dignity Score", f"{data['dignity_score']:.0f}/100")
            
            st.markdown("#### AI-Generated Interpretation")
            st.write(data['explanation'])
            st.markdown("**Workflow Insights:**")
            for ins in data['workflow_insights']:
                st.markdown(f"- {ins}")
            
            st.markdown(f"*{data['disclaimer']}*")
    else:
        st.info("Upload data in the Overview tab to see findings.")

with tab3:
    st.subheader("Resident Directory")
    if st.session_state.analysis_results is not None:
        df_res = st.session_state.df
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_filter = st.multiselect("Filter by Status", options=df_res['status'].unique())
        with col_f2:
            all_rules = set()
            for rlist in df_res['triggered_rules']:
                all_rules.update(rlist)
            rule_filter = st.multiselect("Filter by Triggered Rule", options=list(all_rules))
            
        filtered_df = df_res.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
        if rule_filter:
            # Keep rows that contain AT LEAST ONE of the filtered rules
            mask = filtered_df['triggered_rules'].apply(lambda rules: any(rf in rules for rf in rule_filter))
            filtered_df = filtered_df[mask]
            
        filtered_df['rule_count'] = filtered_df['triggered_rules'].apply(len)
        
        display_df3 = filtered_df[['resident_id', 'status', 'confidence', 'ambiguous_cause', 'rule_count', 'mobility_score', 'autonomy_score', 'dignity_score']].copy()
        
        st.dataframe(display_df3.style.map(color_status, subset=['status']), use_container_width=True)
        
        # Expandable regulatory notes
        st.markdown("#### Regulatory Notes by Resident")
        for idx, row in filtered_df.iterrows():
            if row['regulatory_notes']:
                with st.expander(f"{row['resident_id']} - Notes"):
                    for rn in row['regulatory_notes']:
                        st.write(f"- {rn}")
    else:
        st.info("Upload data in the Overview tab to see directory.")

with tab4:
    st.subheader("Immutable Audit Log")
    st.info("Audit records are append-only and SHA256-verified for integrity.")
    
    audit_df = logger.get_all_runs()
    if audit_df.empty:
        st.write("No analysis runs recorded yet. Run an analysis to begin the audit trail.")
    else:
        st.dataframe(audit_df, use_container_width=True)

with tab5:
    st.subheader("System Transparency")
    st.write('This tab answers the question: "Who watches the watcher?"')
    
    st.markdown("### Section 1 — All 5 Rules")
    rules_data = [
        {"rule_id": "R1_MOBILITY_SUPPRESSION", "condition": "Steps drop after alert", "threshold": ">40% (High), >30% (Medium)", "justification": "Steps dropping significantly after an alert indicates potential restraint-effect mobility suppression.", "ref": "CMS §483.25(h)", "url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.25"},
        {"rule_id": "R2_CONFINEMENT_SIGNAL", "condition": "Visiting <2 rooms for multiple consecutive days", "threshold": "5+ days (High), 3-4 days (Medium)", "justification": "Indicates potential confinement.", "ref": "CMS §483.10(e)(1)", "url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.10"},
        {"rule_id": "R3_SEDENTARY_SPIRAL", "condition": ">18 hours of sedentary time for multiple days", "threshold": "7+ days (High), 5-6 days (Medium)", "justification": "Strongly correlates with functional decline.", "ref": "CMS §483.25(h)", "url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.25"},
        {"rule_id": "R4_CAREGIVER_OVERDEPENDENCE", "condition": "Caregiver time doubling while steps halve", "threshold": "Care >= 2x AND Steps <= 0.5x", "justification": "Indicates potential learned helplessness.", "ref": "CMS §483.12(a)(2)", "url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-483/subpart-B/section-483.12"},
        {"rule_id": "R5_ALERT_SUPPRESSION_EFFECT", "condition": "Rapid movement drop >40% after a *new* alert", "threshold": "40% drop over 48h window", "justification": "Indicates harmful system intervention effect.", "ref": "NIST AI RMF", "url": "https://airc.nist.gov/RMF"}
    ]
    for rd in rules_data:
        st.markdown(f"**{rd['rule_id']}**: {rd['condition']} | Threshold: {rd['threshold']} | Justification: {rd['justification']} | Reference: [{rd['ref']}]({rd['url']})")
        
    st.markdown("### Section 2 — Scoring Formula")
    score_data = {
         "Rule / Severity": ["R1 High", "R1 Medium", "R2 High", "R2 Medium", "R3 High", "R3 Medium", "R4 Triggered", "R5 High"],
         "Mobility Impact": ["-40", "-20", "0", "0", "-20", "-10", "0", "-30"],
         "Autonomy Impact": ["0", "0", "-35", "-20", "0", "0", "-30", "-15"],
         "Dignity Impact": ["0", "0", "-15", "-10", "-20", "-10", "-40", "0"]
    }
    st.table(pd.DataFrame(score_data))
    
    st.markdown("### Section 3 — What This System Does NOT Do")
    st.markdown("""
    - ❌ Does not determine whether a regulatory violation has occurred
    - ❌ Does not replace clinical judgment or legal review
    - ❌ Does not use machine learning, neural networks, or probabilistic scoring
    - ❌ Does not access, store, or transmit real patient data
    - ❌ Does not make care decisions or modify monitoring settings
    """)
    
    st.markdown("### Section 4 — Self-Assessment Statement")
    st.info("AI Sentinel applies identical rule logic to all residents regardless of demographics, diagnosis, or care level. All thresholds are documented prototype guardrails derived from CMS regulatory language. No adaptive or learned behavior is present in this system.")
    
    st.markdown("### Section 5 — Competitive Context")
    comp_data = {
        "Feature": ["Focus Area", "Healthcare-specific", "Behavioral Monitoring", "CMS-Mapped", "Open Source"],
        "AI Sentinel (MVP)": ["Restraint-effect monitoring", "Yes", "Yes", "Yes", "Yes"],
        "OneTrust": ["General Privacy/Compliance", "Add-on", "No", "Mapped to broad regs", "No"],
        "IBM OpenPages": ["Enterprise GRC", "Add-on", "No", "Requires config", "No"],
        "Microsoft RAI Toolbox": ["ML Model Ops", "No", "No", "No", "Yes"]
    }
    st.table(pd.DataFrame(comp_data))
