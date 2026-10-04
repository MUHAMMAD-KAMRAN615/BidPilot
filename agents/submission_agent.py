from pydantic import BaseModel, Field
from typing import List
from rag.vector_store import TenderVectorStore
from agents.common import get_llm

class ChecklistItem(BaseModel):
    item: str = Field(description="Form name or required document")
    mandatory: bool = Field(description="Is this mandatory for non-rejection")
    submission_format: str = Field(description="e.g. Original notarized copy, PDF upload, CD-ROM")

class SubmissionChecklist(BaseModel):
    items: List[ChecklistItem]

def run_submission_agent(vector_store: TenderVectorStore) -> dict:
    context = vector_store.query("submission requirements mandatory forms affidavits sealed envelope bid security bond copies", k=5)
    llm = get_llm().with_structured_output(SubmissionChecklist)
    prompt = f"""
    You are a Procurement Compliance Inspector. Extract all mandatory submission artifacts, forms, and bonds required:
    
    TENDER SUBMISSION GUIDELINES:
    {context}
    """
    result = llm.invoke(prompt)
    if isinstance(result, dict):
        return result
    return result.model_dump()
