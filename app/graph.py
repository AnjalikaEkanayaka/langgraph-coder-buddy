from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.agents.planner import planner_node
from app.agents.architect import architect_node
from app.agents.coder import coder_node

def should_continue(state):
    tasks = state.get("tasks") or []
    idx = int(state.get("current_task_index") or 0)

    if state.get("error"):
        return "end"
    
    if idx < len(tasks):
        return "continue"

    return "end"

def build_graph():
    g = StateGraph(GraphState)

    # Add a node named "planner"
    g.add_node("planner", planner_node)
    g.add_node("architect", architect_node)
    g.add_node("coder", coder_node)

    # Define flow: start -> planner -> end
    g.set_entry_point("planner")
    g.add_edge("planner", "architect")
    g.add_edge("architect", "coder")

    g.add_conditional_edges(
        "coder",
        should_continue,
        {
            "continue": "coder",
            "end": END
        }
    )

    return g.compile()
