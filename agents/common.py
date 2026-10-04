import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )
    
    # Use standard gemini-2.5-flash which is active and supports structured output
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature,
        google_api_key=api_key,
        max_retries=6,
    )
