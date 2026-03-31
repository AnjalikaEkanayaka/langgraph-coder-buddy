from app.llm import get_llm

def planner_node(state):

    print("[Planner] Creating plan...")

    """
    Planner Agent:
    - reads user_request
    - asks the LLM to create a project plan
    - saves it into state["plan"]
    """
    req = (state.get("user_request") or "").strip()
    if not req:
        state["error"] = "user_request is empty"
        state["plan"] = ""
        return state

    llm = get_llm()

    # This is the instruction we give to the AI.
    # We are telling it EXACTLY what we want (structured plan).
    prompt = f"""
You are a senior software engineer.
Create a clear project plan for this request:

REQUEST:
{req}

RULES:
- Keep the plan practical and step-by-step.
- Include: tech stack, files needed, main features, and run instructions.
- Do NOT write full code yet. Only planning.
"""

    try:
        response = llm.invoke(prompt)
        state["plan"] = response.content
        state["error"] = None

        print("[Planner] Plan ready.")
        
    except Exception as ex:
        state["plan"] = ""
        state["error"] = str(ex)

    return state

print("[Planner] Plan ready.")