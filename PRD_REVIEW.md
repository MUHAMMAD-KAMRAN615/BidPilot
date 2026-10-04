# Product Requirements Document (PRD)
## Project: BidPilot — Autonomous Multi-Agent Tender Intelligence Engine
**Document Version:** 2.0  
**Target Event:** Pak Angels & NCEAC Hackathon  
**Live Application:** [https://tenderbidpilot.streamlit.app/](https://tenderbidpilot.streamlit.app/)  
**Repository:** [https://github.com/MUHAMMAD-KAMRAN615/BidPilot](https://github.com/MUHAMMAD-KAMRAN615/BidPilot)

---

## 1. Executive Summary & Problem Statement
Small and Medium Enterprises (SMEs) represent over 90% of global businesses, yet they are systematically disadvantaged in public and enterprise procurement. Reviewing a single 100+ page Request for Proposal (RFP) requires 40+ unbillable hours. Over 40% of submitted bids are disqualified due to overlooked prerequisites, hidden penalty liabilities, or omitted compliance artifacts. 

**BidPilot** is an autonomous multi-agent procurement intelligence copilot. It ingests complex solicitation documents (PDF/TXT), verifies bidder operational credentials, flags liquidated damages and SLA penalties, computes a deterministic 0–100 Bid/No-Bid feasibility score, and drafts technical proposals alongside submission checklists in under 3 minutes.

---

## 2. Target Users & Personas
* **SME Government & IT Contractors (10–250 employees):** Companies bidding on defense, municipal, and enterprise cloud migrations without dedicated full-time legal or bid-writing teams.
* **Proposal & Bid Managers:** Professionals needing accelerated compliance matrices and fast initial technical proposal drafts.
* **Executive Decision-Makers (CEOs/VPs):** Leaders who require explainable, data-backed Bid vs. No-Bid recommendations before committing engineering resources.

---

## 3. Product Architecture & Technical Stack

### Core System Stack
* **Frontend UI & Application Layer:** Streamlit Community Cloud (Python 3.11/3.14).
* **LLM Inference Engine:** Groq API (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile`) with automatic backoff retries.
* **Orchestration Framework:** LangChain (Runnables & Structured Output Parsers).
* **Local Semantic Vector Engine:** ChromaDB paired with local HuggingFace embeddings (`all-MiniLM-L6-v2`) executing on CPU (eliminating remote embedding API quotas and 404 endpoint failures).
* **Document Parsing:** PyPDF with `RecursiveCharacterTextSplitter` (1,000-character chunks, 150-character overlap).

### Multi-Agent Pipeline Workflow
1. **Tender Ingestion:** File upload → SHA-256 hash check → PyPDF extraction → ChromaDB vector indexing.
2. **Tender Intake Agent (`tender_agent.py`):** Extracts solicitation authority, estimated budget, submission deadlines, and high-level project scope.
3. **Eligibility Verification Agent (`eligibility_agent.py`):** Evaluates corporate revenue, security clearances, full-time headcount, and certifications (e.g., ISO9001, SOC 2 Type II) against mandatory RFP prerequisites.
4. **Compliance & Legal Agent (`compliance_agent.py`):** Scans for liquidated damages, punitive clauses, and SLA non-compliance penalties.
5. **Operational Risk Agent (`risk_agent.py`):** Assesses delivery timelines, warranty liabilities, and feasibility bottlenecks.
6. **Supervisor Decision Engine (`supervisor_agent.py`):** Applies mathematical scoring and hard gates to produce a definitive `BID`, `REVIEW`, or `NO_BID` verdict.
7. **Synthesis Agents:**
   * **Proposal Agent (`proposal_agent.py`):** Generates a 5-section Markdown Technical Proposal.
   * **Submission Checklist Agent (`submission_agent.py`):** Generates an interactive audit checklist of required forms, affidavits, and bid bonds.

---

## 4. Deterministic Scoring Logic & Decision Gates

The final recommendation is determined by a weighted calculation that balances capability, compliance, and inverted risk:

$$\text{Final Feasibility Score} = (E \times 0.40) + (C \times 0.35) + ((100.0 - R) \times 0.25)$$

* **$E$ (Eligibility Score, 40% weight):** Quantitative match of corporate qualifications against RFP prerequisites.
* **$C$ (Compliance Posture, 35% weight):** Contractual SLA and penalty posture.
* **$R$ (Risk Factor, 25% weight):** Operational delivery risk (inverted so that $0$ risk awards full points).

### Gate Decision Logic
* **`BID`:** Final Score $\ge 75.0\%$ **AND** `is_eligible == True` (ensures a bid is never recommended if mandatory clearance or revenue prerequisites are unmet).
* **`REVIEW`:** Final Score $\ge 55.0\%$ or score $\ge 75.0\%$ with conditional eligibility.
* **`NO_BID`:** Final Score $< 55.0\%$.

---

## 5. Functional Feature Requirements

| Feature ID | Feature Name | Description & Acceptance Criteria |
| :--- | :--- | :--- |
| **FR-01** | **Solicitation Ingestion** | Accepts `.pdf` and `.txt` up to 200MB. Chunks text into ChromaDB without hitting external rate limits. |
| **FR-02** | **Dynamic Bidder Profiling** | Configurable entity profile (Revenue, Headcount, Clearance, ISO/SOC Accreditations, Capabilities). |
| **FR-03** | **Multi-Agent Evaluation** | Executes 4 domain agents sequentially with 3-second pacing to respect API rate limits. |
| **FR-04** | **Penalty & Liability Extraction** | Identifies specific liquidated damages (e.g., $5,000/day delay fines, uptime forfeiture terms). |
| **FR-05** | **Executive Dashboard** | Color-coded status badge, feasibility score KPI, matched vs. missing qualifications, and penalty alert boxes. |
| **FR-06** | **Proposal Generator** | Drafts a 5-section Technical Bid Proposal ready for preview and one-click `.md` export. |
| **FR-07** | **Submission Checklist** | Produces an interactive checklist of mandatory forms (Form 104, 5% Bid Bond, client references). |

---

## 6. Non-Functional & Reliability Requirements
* **Execution Latency:** Complete multi-agent pipeline completes in under 60 seconds on a standard 50-page RFP.
* **Rate-Limit Resilience:** Includes `max_retries=3` exponential backoff and agent cooldown delays.
* **Dual Output Safety:** Structured output handlers accommodate both Pydantic model dumps and direct JSON dictionaries to avoid runtime attribute crashes.
* **Security & Credential Isolation:** Zero hardcoded API keys. Authentication uses Streamlit Cloud Secrets and environment variables.

---

## 7. Verification & Case Study Validation
* **Tested Solicitation:** RFP-2026-CLOUD-99 (Enterprise Mainframe to FedRAMP Cloud Migration, $4,500,000 budget).
* **Bidder Baseline:** Apex Cyber Cloud Solutions Inc. ($5.5M revenue, 48 employees, Secret clearance, ISO 9001, SOC 2 Type II).
* **Output:**
  * **Score:** 88% — **BID** Recommendation.
  * **Critical Penalties Identified:** $5,000/day delivery delay penalty; 15% billing forfeiture if availability drops below 99.99%.
  * **Artifacts Generated:** 5-section Technical Architecture proposal + interactive checklist for Form 104 and 5% Irrevocable Bid Bond.