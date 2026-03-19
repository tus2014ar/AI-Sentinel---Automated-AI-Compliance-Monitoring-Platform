# AI Sentinel for MyRaina — Stakeholder Demo Script

This script provides step-by-step instructions and talking points for demonstrating the AI Sentinel MVP to clinical, operational, and compliance stakeholders.

---

## Part 1: Context & Value Proposition (2 mins)

**Talking Points:**
> *"Welcome, everyone. Today we are demonstrating the MVP of 'AI Sentinel for MyRaina'. 
> Our goal is to augment our fall-monitoring capabilities without accidentally introducing 'least-restrictive care' compliance risks under CMS guidelines.*
>
> *This tool analyzes mobility and caregiver interaction patterns across the resident cohort. Crucially, we designed this with severe guardrails:*
> *1. It is entirely deterministic — there are NO neural networks making probabilistic decisions.*
> *2. It runs 100% locally on our infrastructure — zero cloud dependency and zero patient data leaves the network.*
> *3. It uses GenAI exclusively as a translation layer to turn deterministic rule outputs into plain English 'Workflow Insights'. It does not hallucinate findings."*

---

## Part 2: The Streamlit Dashboard Demo (5 mins)

**Preparation:**
Ensure the Streamlit app is running (`python -m streamlit run app/main.py`). Open the browser to `http://localhost:8501`.

### Step 1: The Overview Tab
1. Show the blank **Overview** tab. Emphasize the clean interface.
2. Click **Browse files** and upload `data/dataset_normal.csv`.
3. **Talking Point:** *"Here we upload a baseline dataset of residents functioning normally. As expected, the system instantly flags 10 green 'No Issue' cards. No false positives."*
4. Click **Browse files** again and upload `data/dataset_restrained.csv`.
5. **Talking Point:** *"Now, we upload a high-risk dataset where residents experienced mobility declines following sensor alerts. Instantly, the dashboard highlights 10 residents as 'Review Recommended' (🔴). The compliance baseline is immediately visible."*

### Step 2: The Findings Tab
1. Click the **Findings** tab. Select `RES_SEVERE_01` from the dropdown.
2. **Talking Point:** *"If a nurse or compliance officer wants to know WHY a resident was flagged, they come here. The AI generates a plain English explanation and specific Workflow Insights — such as 'Review whether the resident's daily schedule includes opportunities for movement'."*
3. **Action:** Expand the `R1_MOBILITY_SUPPRESSION` accordion.
4. **Talking Point:** *"Because transparency is our priority, clicking these accordions shows exactly which CMS regulation was flagged, the exact metric drop, and our deterministic threshold. We never hide the math."*

### Step 3: The Audit Log Tab
1. Click the **Audit Log** tab.
2. **Talking Point:** *"For legal and compliance defensibility, every single analysis run is immutably logged to a local SQLite database and tracked with a cryptographic SHA-256 hash. If auditors ever ask what the system saw on a specific day, we can prove it."*

### Step 4: System Transparency Tab
1. Click the **System Transparency** tab. 
2. **Talking Point:** *"To answer the question 'Who watches the watcher?', we built this tab. It explicitly lists our 5 operational rules, the exact scoring formula, and a definitive list of things the system 'Does NOT Do' — such as making medical decisions."*

---

## Part 3: The CLI Demo (3 mins)

**Preparation:**
Have your terminal open and navigated to the project root (`AI_Sentinel_MyRaina`).

### Step 1: Bulk Analysis
1. Run the following command:
   ```bash
   python -m src.cli analyze --data data/dataset_restrained.csv
   ```
2. **Talking Point:** *"For our data scientists or automated nightly batch jobs, the tool is fully available via a high-speed Command Line Interface. It instantly processes the cohort into a clean, color-coded table."*

### Step 2: Individual Resident Drill-down
1. Run the following command:
   ```bash
   python -m src.cli analyze --data data/dataset_edge_cases.csv --resident RES_AMBIGUOUS
   ```
2. **Talking Point:** *"We can also drill down into specific edge cases. Notice this output: The system flagged this resident for monitoring but explicitly noted it was an 'Ambiguous Cause' because steps dropped, but there were no alarms. The AI insight immediately recommends ruling out acute health changes before blaming the monitoring workflow. It's smart enough to know what it doesn't know."*

### Step 3: Automated Reporting
1. Run the following command:
   ```bash
   python -m src.cli analyze --data data/dataset_restrained.csv --output-text data/weekly_compliance_report.txt
   ```
2. **Talking Point:** *"Finally, the CLI can automatically flush the entire analysis, including all AI explanations, into a clean text or JSON report for email distribution or integration with other MyRaina systems."*
