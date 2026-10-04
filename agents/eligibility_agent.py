from pydantic import BaseModel, Field
from typing import List
from rag.vector_store import TenderVectorStore
from agents.common import get_llm

class EligibilityReport(BaseModel):
    is_eligible: bool = Field(description="Whether company satisfies mandatory prerequisites")
    eligibility_score: float = Field(description="0 to 100 feasibility rating")
    matched_qualifications: List[str] = Field(description="Requirements satisfied by profile")
    missing_qualifications: List[str] = Field(description="Disqualifying misses or gaps")
    reasoning: str = Field(description="Detailed verification rationale")

def run_eligibility_agent(vector_store: TenderVectorStore, company_profile: dict) -> dict:
    context = vector_store.query("mandatory requirements qualifications past performance certifications revenue clearance", k=5)
    llm = get_llm().with_structured_output(EligibilityReport)
    
    prompt = f"""
    You are an Eligibility Evaluation Agent. Compare this Company Profile against the Tender Requirements.
    
    COMPANY PROFILE:
    Name: {company_profile.get('name')}
    Annual Revenue: ${company_profile.get('annual_revenue')}
    Employees: {company_profile.get('employee_count')}
    Security Clearance: {company_profile.get('security_clearance')}
    Certifications: {company_profile.get('certifications')}
    Competencies: {company_profile.get('core_competencies')}
    
    TENDER PREREQUISITES CONTEXT:
    {context}
    """
    
    result = llm.invoke(prompt)
    
    # Safe return: supports both Pydantic instance and direct dict from Groq
    if isinstance(result, dict):
        return result
    return result.model_dump()
