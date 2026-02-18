import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

def get_llm():
    """
    Creates and returns the Groq chat model object.
    We keep it in one place so later we can swap Groq -> another API easily.
    """
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Put it in your .env file.")

    # Beginner note:
    # temperature controls randomness:
    #   0.0 = very strict / deterministic
    #   0.2 = a little creative but still stable
    
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=api_key,
        max_tokens=800  
    )
