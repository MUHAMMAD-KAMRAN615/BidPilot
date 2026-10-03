import streamlit as st
import os
import tempfile
from rag.vector_store import TenderVectorStore
from agents.supervisor_agent import run_pipeline
from agents.proposal_agent import run_proposal_agent
from agents.submission_agent import run_submission_agent

# Page configuration
st.set_page_config(
    page_title="BidPilot | Autonomous Tender Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-container {
        padding: 1.8rem 2.2rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        font-weight: 400;
    }

    .kpi-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
    }
    
    .badge-bid {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    .badge-review {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.3);
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    .badge-nobid {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    .penalty-box {
        background: rgba(244, 63, 94, 0.08);
        border-left: 4px solid #F43F5E;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    .risk-box {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid #EF4444;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Application Header Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🛡️ BidPilot Procurement Intelligence</div>
    <div class="hero-subtitle">Autonomous Multi-Agent Evaluation, Compliance Matrix & Proposal Synthesis System</div>
</div>
""", unsafe_allow_html=True)

# API Key Authentication Setup
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
try:
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/combo-chart.png", width=64)
    st.markdown("### 🏢 Bidder Profile")
    st.caption("Active operational baseline compared against tender prerequisites.")
    
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter AI Studio Key...")
    
    company_name = st.text_input("Entity Name", "Apex Cyber Cloud Solutions Inc.")
    annual_revenue = st.number_input("Annual Revenue ($)", value=5500000.0, step=500000.0)
    employee_count = st.number_input("Full-time Employees", value=48, step=5)
    security_clearance = st.selectbox("Facility Security Clearance", ["None", "Secret", "Top Secret"], index=1)
    certifications = st.multiselect(
        "Accreditations", 
        ["ISO9001", "SOC2_TYPE_II", "CMMI_LEVEL_3", "FedRAMP", "NIST_800_171"], 
        default=["ISO9001", "SOC2_TYPE_II"]
    )
    competencies = st.text_area("Core Capabilities", "Cloud Architecture, Database Migration, DevSecOps")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key

profile = {
    "name": company_name,
    "annual_revenue": annual_revenue,
    "employee_count": employee_count,
    "security_clearance": security_clearance,
    "certifications": certifications,
    "core_competencies": [c.strip() for c in competencies.split(",") if c.strip()]
}

# Upload Interface
upload_col, info_col = st.columns([2, 1])

with upload_col:
    uploaded_file = st.file_uploader("📥 Ingest Solicitation Document (PDF or TXT)", type=["pdf", "txt"])

with info_col:
    st.info("**Evaluation Pipeline**\n- 📄 RAG Semantic Ingestion\n- ⚖️ Compliance & SLA Extraction\n- 🛡️ Corporate Clearance Verification\n- 📊 Weighted 0–100 Bid/No-Bid Decision")

# State reset logic on file removal or change
if "current_file" in st.session_state:
    if uploaded_file is None or uploaded_file.name != st.session_state["current_file"]:
        for key in ["results", "proposal", "checklist", "tender_id", "profile"]:
            st.session_state.pop(key, None)
        if uploaded_file is None:
            del st.session_state["current_file"]

if uploaded_file:
    st.session_state["current_file"] = uploaded_file.name

if uploaded_file and not api_key:
    st.warning("⚠️ Enter your Gemini API Key in the left sidebar to initialize the multi-agent system.")

if uploaded_file and api_key:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    tender_id = uploaded_file.name.replace(".", "_")

    if st.button("🚀 Run Multi-Agent Evaluation", type="primary", use_container_width=True):
        with st.status("🔍 Analyzing Tender Solicitation...", expanded=True) as status:
            st.write("Chunking document & generating semantic embeddings...")
            vs = TenderVectorStore(tender_id)
            vs.ingest_document(tmp_path)
            
            st.write("Running Supervisor & Domain Agents...")
            results = run_pipeline(tender_id, profile)
            
            st.session_state["results"] = results
            st.session_state["tender_id"] = tender_id
            st.session_state["profile"] = profile
            
            # Flush older generated artifacts
            st.session_state.pop("proposal", None)
            st.session_state.pop("checklist", None)
            
            status.update(label="✅ Evaluation Completed", state="complete", expanded=False)

# Analysis Dashboard Display
if "results" in st.session_state:
    res = st.session_state["results"]
    st.divider()

    # Top Executive KPIs
    score = res["bid_score"]
    decision = res["bid_decision"]
    badge_style = "badge-bid" if decision == "BID" else "badge-review" if decision == "REVIEW" else "badge-nobid"

    col_score, col_summary = st.columns([1, 2.5])
    with col_score:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="{badge_style}">{decision} RECOMMENDATION</span>
            <h1 style="font-size: 3.2rem; font-weight: 800; margin: 0.8rem 0; color: white;">{score}%</h1>
            <p style="color: #94A3B8; font-size: 0.85rem; margin: 0;">Weighted Feasibility Score</p>
        </div>
        """, unsafe_allow_html=True)

    with col_summary:
        st.subheader("Executive Assessment")
        st.write(res["summary"])
        st.caption(f"**Assessing Entity:** {profile['name']} | **Clearance Tier:** {profile['security_clearance']}")

    # Tabs for Agent Detail
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🛡️ Eligibility Verification", "⚖️ Legal & SLA Penalties", "⚠️ Operational Risk"])

    with t1:
        e = res.get("eligibility", {})
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Eligibility Rating", f"{e.get('eligibility_score', 0)}%")
        with c2:
            st.write(f"**Verification Rationale:** {e.get('reasoning', 'N/A')}")
        
        st.divider()
        m_col, g_col = st.columns(2)
        with m_col:
            st.markdown("##### ✅ Matched Qualifications")
            for item in e.get("matched_qualifications", []):
                st.success(item)
        with g_col:
            st.markdown("##### ❌ Qualification Gaps")
            missing = e.get("missing_qualifications", [])
            if missing:
                for item in missing:
                    st.error(item)
            else:
                st.caption("No disqualifying gaps identified.")

    with t2:
        c = res.get("compliance", {})
        st.metric("Compliance Posture", f"{c.get('compliance_score', 0)}%")
        st.markdown("##### 🚨 Penalties & Damages Identified")
        penalties = c.get("penalties_identified", [])
        if penalties:
            for p in penalties:
                st.markdown(f'<div class="penalty-box">⚠️ {p}</div>', unsafe_allow_html=True)
        else:
            st.success("No punitive damages or critical SLA liquidated liabilities identified.")

    with t3:
        r = res.get("risk", {})
        st.metric("Overall Risk Level", r.get("overall_risk_level", "UNKNOWN"))
        st.markdown("##### ⚡ Key Risk Drivers")
        for risk in r.get("identified_risks", []):
            st.markdown(f'<div class="risk-box">🔴 {risk}</div>', unsafe_allow_html=True)

    # Document Generators Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📑 Generation Suite")
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        if st.button("📄 Generate Technical Proposal Draft", use_container_width=True):
            with st.spinner("Drafting full proposal..."):
                vs = TenderVectorStore(st.session_state["tender_id"])
                proposal = run_proposal_agent(vs, st.session_state["profile"], res["summary"])
                st.session_state["proposal"] = proposal

    with b_col2:
        if st.button("📋 Generate Submission Checklist", use_container_width=True):
            with st.spinner("Auditing mandatory forms and certifications..."):
                vs = TenderVectorStore(st.session_state["tender_id"])
                chk = run_submission_agent(vs)
                st.session_state["checklist"] = chk.get("items", [])

    # Proposal Display Block
    if "proposal" in st.session_state:
        st.divider()
        st.subheader("📄 Generated Technical Proposal")
        raw_proposal = st.session_state["proposal"]

        if isinstance(raw_proposal, list):
            text_blocks = [
                b.get("text", "") if isinstance(b, dict) and b.get("type") == "text" else str(b)
                for b in raw_proposal
            ]
            clean_proposal = "\n".join(text_blocks)
        else:
            clean_proposal = str(raw_proposal)

        with st.expander("Preview Proposal Document", expanded=True):
            st.markdown(clean_proposal)

        st.download_button(
            label="💾 Download Proposal as Markdown (.md)",
            data=clean_proposal,
            file_name=f"{st.session_state['tender_id']}_Proposal.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Checklist Display Block
    if "checklist" in st.session_state:
        st.divider()
        st.subheader("📋 Mandatory Submission Checklist")
        st.caption("Review and verify all required documentation prior to final tender submission.")
        
        for idx, item in enumerate(st.session_state["checklist"]):
            st.checkbox(
                f"**{item['item']}** — Format: `{item.get('submission_format', 'PDF')}`", 
                key=f"chk_{idx}",
                value=False
            )
