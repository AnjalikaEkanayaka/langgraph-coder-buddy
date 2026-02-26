import json
from app.llm import get_llm

def architect_node(state):
    """
    Architect Agent:
    - reads state["plan"]
    - creates a structured list of file tasks
    - saves it into state["tasks"]
    """

    plan = (state.get("plan") or "").strip()
    if not plan:
        state["error"] = "plan is empty (planner did not produce a plan)"
        state["tasks"] = []
        return state

    llm = get_llm(max_tokens=1500)

    # We ask the LLM to output STRICT JSON so our code can parse it.
    # This is a key skill in agent systems:
    # - human text is hard to use
    # - structured JSON is easy to use
    prompt = f"""
You are a software architect.

Convert the following project plan into a list of file-writing tasks.

PLAN:
{plan}

Return ONLY valid JSON.
Do NOT include explanations.
Do NOT include markdown.
Do NOT include comments.

The JSON must follow this EXACT format:

{{
  "tasks": [
    {{
      "file_path": "index.html",
      "purpose": "short reason why this file exists",
      "requirements": [
        "requirement 1",
        "requirement 2"
      ]
    }}
  ]
}}
"""

    try:
        resp = llm.invoke(prompt)
        text = resp.content.strip()

        # DEBUG: print raw architect output
        print("\n--- RAW ARCHITECT OUTPUT ---")
        print(text)
        print("--- END RAW OUTPUT ---\n")

        # Remove markdown fences if model adds them
        if "```" in text:
            text = text.replace("```json", "").replace("```", "").strip()

        # Extract JSON safely 
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end+1]

        data = json.loads(text)

        state["tasks"] = data.get("tasks", [])
        state["current_task_index"] = 0
        state["error"] = None

    except Exception as ex:
        state["tasks"] = []
        state["error"] = "Architect failed: " + str(ex)

    return state
