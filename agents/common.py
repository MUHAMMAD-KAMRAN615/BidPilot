import os
from langchain_groq import ChatGroq

def get_llm(temperature: float = 0.0) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY", "")
    
    # Exact model ID without any 'models/' prefix
    # llama-3.1-8b-instant is active across all free Groq tiers and supports structured outputs
    return ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3,
    )
