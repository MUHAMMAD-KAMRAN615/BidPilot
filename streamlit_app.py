import streamlit as st
import os
import tempfile
from rag.vector_store import TenderVectorStore
from agents.supervisor_agent import run_pipeline
from agents.proposal_agent import run_proposal_agent
from agents.submission_agent import run_submission_agent

st.set_page_config(page_title="BidPilot - Tender AI", page_icon="📑", layout="wide")

st.title("📑 BidPilot: Multi-Agent Tender Intelligence")
st.caption("AI-Powered Autonomous Tender Analysis & Proposal Generator")

# Retrieve API key from environment, Streamlit Secrets, or sidebar input
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

try:
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key (Google AI Studio)", type="password")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key

# Bidder Profile Configuration
st.sidebar.header("🏢 Bidder Company Profile")
company_name = st.sidebar.text_input("Company Name", "Apex Cyber Cloud Solutions Inc.")
annual_revenue = st.sidebar.number_input("Annual Revenue ($)", value=5500000.0)
employee_count = st.sidebar.number_input("Employee Count", value=48)
security_clearance = st.sidebar.selectbox("Security Clearance", ["None", "Secret", "Top Secret"], index=1)
certifications = st.sidebar.multiselect("Certifications", ["ISO9001", "SOC2_TYPE_II", "CMMI_LEVEL_3", "FedRAMP"], default=["ISO9001", "SOC2_TYPE_II"])
competencies = st.sidebar.text_area("Core Competencies", "Cloud Architecture, Database Migration, DevSecOps")

profile = {
    "name": company_name,
    "annual_revenue": annual_revenue,
    "employee_count": employee_count,
    "security_clearance": security_clearance,
    "certifications": certifications,
    "core_competencies": [c.strip() for c in competencies.split(",") if c.strip()]
}

# Tender Upload Section
uploaded_file = st.file_uploader("Upload Tender Document (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file and not api_key:
    st.warning("Please provide your OpenAI API key in the sidebar to proceed.")

if uploaded_file and api_key:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    tender_id = uploaded_file.name.replace(".", "_")
    
    if st.button("🚀 Execute Multi-Agent Evaluation", type="primary"):
        with st.spinner("Indexing tender sections and running multi-agent checks..."):
            vs = TenderVectorStore(tender_id)
            vs.ingest_document(tmp_path)
            results = run_pipeline(tender_id, profile)
            st.session_state["results"] = results
            st.session_state["tender_id"] = tender_id
            st.session_state["profile"] = profile

if "results" in st.session_state:
    res = st.session_state["results"]
    st.divider()

    # Executive Score Banner
    col1, col2 = st.columns([1, 2])
    with col1:
        color = "green" if res["bid_decision"] == "BID" else "orange" if res["bid_decision"] == "REVIEW" else "red"
        st.metric(label="Overall Bid Score", value=f"{res['bid_score']}%", delta=res["bid_decision"])
    with col2:
        st.subheader("Executive Assessment")
        st.write(res["summary"])

    # Detailed Agent Outputs
    tab1, tab2, tab3 = st.tabs(["🛡️ Eligibility", "⚖️ Compliance & SLA", "⚠️ Risk Analysis"])
    
    with tab1:
        st.write(f"**Eligibility Score:** {res['eligibility'].get('eligibility_score')}%")
        st.write(f"**Reasoning:** {res['eligibility'].get('reasoning')}")
        st.success("**Matched Qualifications:** " + ", ".join(res['eligibility'].get('matched_qualifications', [])))
        if res['eligibility'].get('missing_qualifications'):
            st.error("**Missing Items:** " + ", ".join(res['eligibility'].get('missing_qualifications', [])))

    with tab2:
        st.write(f"**Compliance Score:** {res['compliance'].get('compliance_score')}%")
        st.write("**Penalties & Damages Found:**")
        for p in res['compliance'].get('penalties_identified', []):
            st.warning(p)

    with tab3:
        st.write(f"**Risk Level:** {res['risk'].get('overall_risk_level')}")
        for r in res['risk'].get('identified_risks', []):
            st.error(r)

    st.divider()
    b_col1, b_col2 = st.columns(2)
    
    with b_col1:
        if st.button("📄 Generate Technical Proposal"):
            with st.spinner("Drafting proposal..."):
                vs = TenderVectorStore(st.session_state["tender_id"])
                proposal = run_proposal_agent(vs, st.session_state["profile"], res["summary"])
                st.session_state["proposal"] = proposal
                
    with b_col2:
        if st.button("📋 Generate Submission Checklist"):
            with st.spinner("Extracting mandatory submission criteria..."):
                vs = TenderVectorStore(st.session_state["tender_id"])
                chk = run_submission_agent(vs)
                st.session_state["checklist"] = chk.get("items", [])

    if "proposal" in st.session_state:
        st.subheader("Generated Proposal Draft")
        raw_proposal = st.session_state["proposal"]
        
        # Unpack list format if cached in session
        if isinstance(raw_proposal, list):
            text_blocks = [
                b.get("text", "") if isinstance(b, dict) and b.get("type") == "text" else str(b)
                for b in raw_proposal
            ]
            clean_proposal = "\n".join(text_blocks)
        else:
            clean_proposal = str(raw_proposal)
            
        st.markdown(clean_proposal)

    if "checklist" in st.session_state:
        st.subheader("Submission Checklist")
        for item in st.session_state["checklist"]:
            st.checkbox(f"**{item['item']}** — Format: `{item['submission_format']}`", value=False)