from rag.vector_store import TenderVectorStore
from agents.common import get_llm

def run_proposal_agent(vector_store: TenderVectorStore, company_profile: dict, tender_summary: str) -> str:
    context = vector_store.query("scope of work statement of work technical requirements deliverables objectives", k=6)
    llm = get_llm()
    prompt = f"""
    You are a Chief Proposal Engineer. Write a comprehensive, professional Technical Bid Proposal draft formatted in Markdown.
    
    BIDDER DETAILS:
    Company: {company_profile.get('name')}
    Competencies: {company_profile.get('core_competencies')}
    Certifications: {company_profile.get('certifications')}
    
    TENDER SCOPE:
    Summary: {tender_summary}
    Requirements Context:
    {context}
    
    STRUCTURE:
    # 1. Executive Summary
    # 2. Company Profile & Past Qualifications
    # 3. Technical Solution & Architecture
    # 4. Implementation Methodology & Milestones
    # 5. Risk Management & Quality Assurance
    """
    response = llm.invoke(prompt)
    
    # Handle list-based content returned by newer Gemini SDKs
    if isinstance(response.content, list):
        text_parts = []
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "\n".join(text_parts)
        
    return str(response.content)