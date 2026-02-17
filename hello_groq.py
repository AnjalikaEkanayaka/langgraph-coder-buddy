import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

def main():
    load_dotenv()  # loads GROQ_API_KEY from .env into environment variables

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("ERROR: GROQ_API_KEY not found. Put it in .env (same folder).")

    # A lightweight, common Groq model name.
    # If Groq rejects it, we’ll switch to one available on your account.
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=api_key
    )

    msg = llm.invoke("Say hello in one short sentence and tell me you are ready.")
    print(msg.content)

if __name__ == "__main__":
    main()
