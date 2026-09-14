import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    return ChatGoogleGenerativeAI(
        model="models/gemini-3.6-flash",
        temperature=temperature,
        google_api_key=api_key,
    )