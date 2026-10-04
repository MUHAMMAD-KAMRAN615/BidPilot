import time
from rag.vector_store import TenderVectorStore
from agents.tender_agent import run_tender_agent
from agents.eligibility_agent import run_eligibility_agent
from agents.compliance_agent import run_compliance_agent
from agents.risk_agent import run_risk_agent

def run_pipeline(tender_id: str, company_profile: dict) -> dict:
    vector_store = TenderVectorStore(tender_id)
    
    # 1. Tender Research
    tender_meta = run_tender_agent(vector_store)
    time.sleep(3)  # Rate-limit cooldown
    
    # 2. Eligibility Verification
    eligibility = run_eligibility_agent(vector_store, company_profile)
    time.sleep(3)  # Rate-limit cooldown
    
    # 3. Compliance Matrix Extraction
    compliance = run_compliance_agent(vector_store)
    time.sleep(3)  # Rate-limit cooldown
    
    # 4. Risk Profile Assessment
    risk = run_risk_agent(vector_store, company_profile)
    
    # 5. Weighted Score Calculation
    e_score = eligibility.get("eligibility_score", 50.0)
    c_score = compliance.get("compliance_score", 50.0)
    r_score = risk.get("risk_score", 50.0)
    
    final_score = round((e_score * 0.40) + (c_score * 0.35) + ((100.0 - r_score) * 0.25), 1)
    
    if final_score >= 75.0 and eligibility.get("is_eligible", False):
        decision = "BID"
    elif final_score >= 55.0:
        decision = "REVIEW"
    else:
        decision = "NO_BID"
        
    return {
        "tender_meta": tender_meta,
        "eligibility": eligibility,
        "compliance": compliance,
        "risk": risk,
        "bid_score": final_score,
        "bid_decision": decision,
        "summary": tender_meta.get("summary", "")
    }
