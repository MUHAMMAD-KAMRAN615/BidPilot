import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    api_key = (
        os.getenv("GEMINI_API_KEY") 
        or os.getenv("GOOGLE_API_KEY") 
        or os.getenv("OPENAI_API_KEY")
    )
    
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash-lite",  # Higher rate limit allowance
        temperature=temperature,
        google_api_key=api_key,
        max_retries=6,  # Automatically pauses and retries when a 429 occurs
    )
