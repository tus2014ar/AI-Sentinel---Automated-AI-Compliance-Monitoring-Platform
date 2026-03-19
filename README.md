# AI Sentinel - Automated AI Compliance & Monitoring Platform

### AI Sentinel for MyRaina (Fall Management Technology)

![Penn State Nittany AI Challenge 2026](https://img.shields.io/badge/Penn%20State-Nittany%20AI%20Challenge%202026-001E62?style=flat-square)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![Local-First](https://img.shields.io/badge/Architecture-Local--First-green?style=flat-square)
![CMS-Compliant](https://img.shields.io/badge/Regulation-CMS%20Mapped-orange?style=flat-square)
![No Black Box](https://img.shields.io/badge/AI-No%20Black%20Box-red?style=flat-square)

> Autonomous compliance agents that detect ethical, privacy, and cybersecurity risks in AI systems — with MyRaina fall-monitoring as the first live use case.

---

## 🎯 The Problem

Modern organizations depend on AI but face mounting ethical misuse, privacy breaches, and regulatory risk across every sector. Compliance is manual, fragmented, and consistently unable to keep pace with evolving standards — including HIPAA, the EU AI Act, and CMS federal care regulations. Current tools audit policy documents. None monitor the behavioral and operational effects of AI systems in real time, at the resident or user level, where harm actually occurs.

---

## Our Solution

AI Sentinel is an automated compliance and monitoring platform built on specialized agents for risk detection, ethical evaluation, continuous auditing, and incident response. Each agent targets a specific compliance domain — and a meta-agent orchestrates their findings into a unified, explainable output that compliance teams can act on immediately. Unlike existing governance tools that operate at the policy level, AI Sentinel monitors for patterns that signal risk before they escalate.

---

## Use Case 1 — MyRaina: Fall-Monitoring Compliance

This is the MVP implemented for the Penn State Nittany AI Challenge 2026.

MyRaina monitors residents in skilled nursing facilities to reduce fall risk. CMS federal regulations — 42 CFR §483.25(h), §483.10(e)(1), and §483.12(a)(2) — require that monitoring interventions remain least-restrictive and do not inhibit resident autonomy or freedom of movement. AI Sentinel analyzes resident mobility and caregiver interaction patterns to detect when fall-monitoring workflows may be creating unintended restraint-effect patterns — without making legal determinations or replacing clinical judgment.

---

## ⚙️ How It Works — MyRaina MVP

```
Resident Activity CSV (14-field daily log)
              ↓
  Deterministic Rule Engine
  (5 CMS-mapped behavioral rules)
              ↓
  Classification Engine
  no_issue | monitor | review_recommended
  + confidence level + ambiguous_cause flag
              ↓
  Hybrid AI Explanation Layer
  (Ollama Local GenAI for summaries + Deterministic Templates for workflows)
              ↓
  ┌─────────────────┬──────────────┬──────────────────┐
  Streamlit Dashboard   CLI Export    SQLite Audit Log
  (5-tab compliance UI) (JSON + Text)  (SHA-256 verified)
```

**AI is used exclusively to translate deterministic rule triggers into plain English compliance summaries using a local LLM via Ollama. It is constrained by strict templating and never makes independent risk decisions. If the local LLM is down, it safely falls back to a 100% deterministic template engine.**

---

## 🔍 Detection Rules

| Rule | Condition | Clinical Basis | Regulation |
|------|-----------|----------------|------------|
| Mobility Suppression | Steps drop >30% within 7 days of alert | Aligns with PT reassessment threshold for meaningful functional mobility change | CMS §483.25(h) |
| Confinement Signal | Rooms visited <2 for 3+ consecutive days | Spatial restriction indicator consistent with CMS Appendix PP freedom-of-movement concern | CMS §483.10(e)(1) |
| Sedentary Spiral | Sedentary time >18hrs for 5+ consecutive days | Immobility risk level associated with deconditioning and pressure injury onset in geriatric care | CMS §483.25(h) |
| Caregiver Overdependence | Caregiver time doubles while steps halve (14-day window) | Pattern consistent with learned helplessness and over-assistance in long-term care literature | CMS §483.12(a)(2) |
| Alert Suppression Effect | Movement events drop >40% within 48hrs of new alert type | Rapid behavioral change following system intervention — consistent with fear-of-movement response | NIST AI RMF |

> **How Thresholds Were Derived**
> CMS defines restraint effect qualitatively — not numerically. To bridge this gap, we used **Gemini Pro 3.1** to conduct a structured synthesis of CMS Appendix PP guidance, MDS 3.0 Section P functional mobility indicators, and peer-reviewed clinical literature on mobility decline in long-term care settings. Gemini Pro 3.1 was prompted to identify the earliest measurable behavioral signals associated with fear-of-movement, learned helplessness, and functional decline — and to map those signals to the specific CFR citations governing least-restrictive care.
>
> The resulting thresholds represent **clinically informed detection boundaries** derived from regulatory language and mobility research — not arbitrary cutoffs. For example, the 30% step decline threshold for Mobility Suppression aligns with clinical definitions of meaningful functional mobility change used in physical therapy reassessment protocols. The 18-hour sedentary threshold for Sedentary Spiral corresponds to immobility risk levels associated with pressure injury and deconditioning onset in geriatric care literature.
>
> All thresholds are documented, justified, and visible in the System Transparency tab. They are applied consistently across all residents regardless of diagnosis, demographics, or care level. Clinical and compliance review is required before any action is taken on a flagged finding.

---

## Quick Start

**Requirements:** Python 3.9+ and Ollama (for the local LLM agent).

> 📋 All data scenarios are structured around CMS §483.25(h), §483.10(e)(1), and §483.12(a)(2) behavioral patterns. No real resident data is used at any stage.

**1. Clone the repository:**
```bash
git clone <your-github-repo-url>
cd AI_Sentinel_MyRaina
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Install & Start Ollama (for GenAI Explainability):**
Because AI Sentinel runs 100% locally to protect patient privacy, it leverages Ollama to run the Llama 3 model directly on your machine.
- Download Ollama from [ollama.com](https://ollama.com/)
- Open a terminal and run the following command to download and start the model:
  ```bash
  ollama run llama3
  ```
*(Note: If Ollama is not running, the dashboard will simply fall back to its safe, pre-scripted deterministic templates without crashing).*

**4. Generate CMS scenario data:**
```bash
python data/generate_data.py
```
Generates four CMS-based scenario CSV files in `data/`: `dataset_normal.csv`, `dataset_at_risk.csv`, `dataset_restrained.csv`, `dataset_edge_cases.csv`.

**5. Launch the Streamlit dashboard:**
```bash
python -m streamlit run app/main.py
```
Opens automatically at `http://localhost:8501`

**6. Run the CLI:**

Analyze a full dataset:
```bash
python -m src.cli analyze --data data/dataset_restrained.csv
```

Drill into a specific resident:
```bash
python -m src.cli analyze --data data/dataset_edge_cases.csv --resident RES_AMBIGUOUS
```

Export a compliance report to JSON:
```bash
python -m src.cli analyze --data data/dataset_restrained.csv --output-json results.json
```

Export a plain-text report:
```bash
python -m src.cli analyze --data data/dataset_restrained.csv --output-text report.txt
```

Check version:
```bash
python -m src.cli --version
```

---

## 📁 Project Structure

```text
AI_Sentinel_MyRaina/
├── app/
│   └── main.py                  # 5-tab Streamlit compliance dashboard
├── src/
│   ├── models/
│   │   ├── resident_data.py     # ResidentRecord dataclass (14 fields)
│   │   └── analysis_result.py   # AnalysisResult dataclass (11 fields)
│   ├── rules/
│   │   ├── mobility_suppression.py      # Rule 1 — CMS §483.25(h)
│   │   ├── confinement_signal.py        # Rule 2 — CMS §483.10(e)(1)
│   │   ├── sedentary_spiral.py          # Rule 3 — CMS §483.25(h)
│   │   ├── caregiver_overdependence.py  # Rule 4 — CMS §483.12(a)(2)
│   │   ├── alert_suppression_effect.py  # Rule 5 — NIST AI RMF
│   │   └── __init__.py          # run_all_rules() orchestrator
│   ├── engine/
│   │   └── analyzer.py          # AnalyzerEngine — classification + scoring
│   ├── ai_explainer/
│   │   └── explainer.py         # Hybrid Ollama GenAI + Deterministic template 
│   ├── audit_logger.py          # SQLite SHA-256 compliance ledger
│   └── cli.py                   # Typer command-line interface
├── data/
│   ├── generate_data.py         # CMS scenario data generator (seed=42)
│   ├── dataset_normal.csv       # Scenario: stable care, no flags expected
│   ├── dataset_at_risk.csv      # Scenario: early-warning CMS concern patterns
│   ├── dataset_restrained.csv   # Scenario: strong restraint-effect indicators + PII test
│   └── dataset_edge_cases.csv   # Scenario: low baseline, nulls, recovery, ambiguous cause
├── tests/
│   ├── test_rules.py            # Unit tests for all 5 rules
│   └── test_engine.py           # Integration tests for classification engine
├── requirements.txt
└── README.md
```

---

## 🖥️ Dashboard — 5 Tabs

- **Overview** — Three primary status cards (No Issue / Monitor / Review Recommended) dominate the view, with a color-coded resident summary table and a "Run on Real Data" placeholder for live MyRaina integration.
- **Findings** — Per-resident rule explorer with expandable sections for each triggered rule showing metric value, threshold, regulation reference, clickable CFR URL, and threshold justification.
- **Residents** — Full resident table with status pills, confidence levels, sub-scores, and filterable sidebar by status or triggered rule.
- **Audit Log** — Append-only SQLite history of every analysis run, SHA-256 hash verified, with no delete capability — tamper-evident by design.
- **System Transparency** — Every rule, threshold, justification, and regulation source fully documented; includes "What This System Does NOT Do" list and a self-assessment statement answering the question: *who watches the watcher?*

---

## Design Principles

- **Deterministic Core** — All risk classifications are produced by explicit if/then rules mapped to CMS federal regulations. No machine learning, no neural networks, and no probabilistic scoring are used anywhere in the classification pipeline. Every output is traceable to a specific line of code.

- **Local-First Architecture** — The entire system runs on local infrastructure with zero cloud dependencies. No resident data ever leaves the secure network, and no API keys or external services are required to operate the tool.

- **Hybrid Explainable AI** — Generative AI is restricted strictly to translating deterministic rule outputs into plain-English explanations using a local Ollama LLM. It cannot modify classifications, introduce new findings, or hallucinate risk indicators not produced by the rule engine. If the LLM goes offline, the system safely falls back to a 100% deterministic text engine.

- **Immutable Audit Trail** — Every analysis run is permanently logged to a local SQLite database with a SHA-256 cryptographic hash. Records are append-only — there is no delete function — ensuring tamper-evident compliance documentation for regulatory review.

---

## Platform Roadmap

AI Sentinel is designed as a multi-use-case compliance platform. MyRaina is Use Case 1.

- **Use Case 2 — HIPAA Compliance Monitoring:** Detect privacy-risk patterns in EHR access logs, flagging anomalous data access, unauthorized disclosure patterns, and minimum-necessary violations in real time.
- **Use Case 3 — EU AI Act Readiness:** Assess high-risk AI system deployments against EU AI Act obligations including transparency requirements, human oversight provisions, and prohibited practice detection.
- **Use Case 4 — Cybersecurity Anomaly Detection:** Identify behavioral anomalies in AI-integrated workflows using pattern recognition and reinforcement learning to surface proactive threat indicators before incident escalation.

---

## Built For

**Penn State Nittany AI Challenge 2026**
Challenge Category: Technology & Software + Social Impact
MVP Code Deadline: March 19, 2026
In-Person Demo: March 25–27, 2026

---

## ⚠️ Disclaimer

This prototype was built for the Penn State Nittany AI Challenge. It does not constitute medical advice, legal opinion, or a determination of regulatory violation. All findings should be reviewed by qualified clinical and compliance staff.
