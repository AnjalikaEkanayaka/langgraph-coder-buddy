from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.agents.planner import planner_node
from app.agents.architect import architect_node
from app.agents.coder import coder_node
from app.agents.reviewer import reviewer_node


def route_after_reviewer(state):
    """
    This function decides what happens AFTER reviewer runs.

    It returns one of these strings:
    - "fix"      -> go back to coder to fix the same file
    - "continue" -> go back to coder to generate the next file
    - "end"      -> stop the graph
    """
    if state.get("error"):
        return "end"

    # If reviewer asked for a fix, coder should regenerate that file
    fix_file = (state.get("fix_file_path") or "").strip()
    if fix_file:
        return "fix"

    # Otherwise, if tasks still remain, continue generating next file
    tasks = state.get("tasks") or []
    idx = int(state.get("current_task_index") or 0)
    if idx < len(tasks):
        return "continue"

    return "end"


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("planner", planner_node)
    g.add_node("architect", architect_node)
    g.add_node("coder", coder_node)
    g.add_node("reviewer", reviewer_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "architect")
    g.add_edge("architect", "coder")

    # After coder writes a file, reviewer checks it
    g.add_edge("coder", "reviewer")

    # After reviewer, decide where to go next
    g.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {
            "fix": "coder",
            "continue": "coder",
            "end": END
        }
    )

    return g.compile()