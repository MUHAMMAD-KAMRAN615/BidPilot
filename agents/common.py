import os
from groq import Groq
from langchain_groq import ChatGroq

def get_llm(temperature: float = 0.0) -> ChatGroq:
    api_key = (
        os.getenv("GROQ_API_KEY") 
        or os.getenv("OPENAI_API_KEY") 
        or ""
    )
    
    # Priority list of top models on Groq
    candidates = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
    ]
    
    chosen_model = candidates[0]
    
    # Dynamically check models supported by your specific API key
    if api_key:
        try:
            client = Groq(api_key=api_key)
            active_ids = [m.id for m in client.models.list().data]
            for candidate in candidates:
                if candidate in active_ids:
                    chosen_model = candidate
                    break
            else:
                if active_ids:
                    chosen_model = active_ids[0]
        except Exception:
            pass

    return ChatGroq(
        model=chosen_model,
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3,
    )
