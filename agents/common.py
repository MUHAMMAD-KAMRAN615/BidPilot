import os
from langchain_groq import ChatGroq

def get_llm(temperature: float = 0.0) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY", "")
    
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3,
    )
