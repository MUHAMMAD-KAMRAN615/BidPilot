from pydantic import BaseModel, Field
from rag.vector_store import TenderVectorStore
from agents.common import get_llm

class TenderDetails(BaseModel):
    title: str = Field(description="Title of the tender or RFP")
    issuing_authority: str = Field(description="Agency or enterprise publishing the solicitation")
    estimated_budget: str = Field(description="Budget if declared, or 'Not Specified'")
    submission_deadline: str = Field(description="Explicit deadline date and time")
    summary: str = Field(description="High-level operational scope summary")

def run_tender_agent(vector_store: TenderVectorStore) -> dict:
    context = vector_store.query("tender title authority scope submission deadline estimated budget", k=4)
    llm = get_llm().with_structured_output(TenderDetails)
    prompt = f"""
    You are an expert Tender Intake Agent. Extract the basic details from this RFP context:
    
    {context}
    """
    result: TenderDetails = llm.invoke(prompt)
    return result.model_dump()
