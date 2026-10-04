from pydantic import BaseModel, Field
from typing import List
from rag.vector_store import TenderVectorStore
from agents.common import get_llm

class ComplianceReport(BaseModel):
    compliance_score: float = Field(description="0 to 100 compliance posture")
    penalties_identified: List[str] = Field(description="Liquidated damages, fines, SLA deductions")
    mandatory_clauses: List[str] = Field(description="Essential contractual clauses")
    audit_requirements: str = Field(description="Inspection and audit terms")

def run_compliance_agent(vector_store: TenderVectorStore) -> dict:
    context = vector_store.query("liquidated damages penalties SLA guarantees audit termination terms clauses", k=5)
    llm = get_llm().with_structured_output(ComplianceReport)
    prompt = f"""
    You are a Legal & Compliance Bidding Agent. Extract all mandatory liability, SLA penalties, and compliance constraints.
    
    TENDER CONTRACT CONTEXT:
    {context}
    """
    result = llm.invoke(prompt)
    
    # Safe return: supports both Pydantic instance and direct dict from Groq
    if isinstance(result, dict):
        return result
    return result.model_dump()
