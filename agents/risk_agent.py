from pydantic import BaseModel, Field
from typing import List
from rag.vector_store import TenderVectorStore
from agents.common import get_llm

class RiskReport(BaseModel):
    overall_risk_level: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    risk_score: float = Field(description="0 to 100 where 100 is maximum risk")
    identified_risks: List[str] = Field(description="Specific technical, timeline, and operational risks")
    mitigation_strategies: List[str] = Field(description="Direct mitigation recommendations")

def run_risk_agent(vector_store: TenderVectorStore, company_profile: dict) -> dict:
    context = vector_store.query("timeline milestones indemnification warranty liability cap termination for convenience", k=5)
    llm = get_llm().with_structured_output(RiskReport)
    prompt = f"""
    You are an Operational Risk Assessment Agent. Identify project and financial delivery risks for the bidder:
    
    BIDDER CAPABILITY:
    {company_profile.get('core_competencies')}
    
    TENDER RISK CLAUSES & SCHEDULE:
    {context}
    """
    result: RiskReport = llm.invoke(prompt)
    return result.model_dump()
