from app.graph import build_graph
from langchain_groq import ChatGroq
from app.llm import get_llm
import json
import os
import re

def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "project"

def generate_project_name(user_request):
    """
    Ask the LLM to generate a short, cool, relevant project name.
    Falls back to slugify if LLM fails.
    """
    try:
        llm = get_llm(max_tokens=50, temperature=0.7)  # higher temp = more creative

        prompt = f"""
Generate a short, cool project name for this app: "{user_request}"

RULES:
- Max 3 words
- No special characters or spaces (use underscores)
- CamelCase only
- Make it relevant and catchy
- Do NOT include words like "app", "project", "tool"
- Examples: "task_flow", "quick_notes", "budget_lens"

Return ONLY the name. Nothing else.
"""
        resp = llm.invoke(prompt)
        raw = (resp.content or "").strip()

        # Clean it up just in case the model adds extra text
        name = slugify(raw.split("\n")[0])[:30]

        # Fallback if result is empty or too short
        if len(name) < 3:
            return slugify(user_request)[:30]

        return name

    except Exception:
        # If anything fails, fall back to old slugify behavior
        return slugify(user_request)[:30]
    
def main():
    graph = build_graph()

    user_request = input("What do you want to build? ").strip()
    print("[Namer] Generating project name...")
    project_name = generate_project_name(user_request)
    print(f"[Namer] Project name: {project_name}")

    output_dir = os.path.join("generated", project_name)

    initial_state = {
        "user_request": user_request,
        "output_dir": output_dir,
        "created_files": [],
        "current_task_index": 0,

        # Reviewer system state
        "fix_file_path": "",
        "fix_reason": "",
        "fix_attempts": 0
    }

    final_state = graph.invoke(initial_state)

    print("\n========================")
    print("OUTPUT FOLDER")
    print("========================")
    print(output_dir)

    print("\n========================")
    print("FILES CREATED")
    print("========================")
    for f in (final_state.get("created_files") or []):
        print("-", f)

    if final_state.get("error"):
        print("\nERROR:", final_state["error"])

    print("\nDone.")

if __name__ == "__main__":
    main()