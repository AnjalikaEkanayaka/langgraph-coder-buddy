from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.agents.planner import planner_node
from app.agents.architect import architect_node

def build_graph():
    g = StateGraph(GraphState)

    # Add a node named "planner"
    g.add_node("planner", planner_node)
    g.add_node("architect", architect_node)

    # Define flow: start -> planner -> end
    g.set_entry_point("planner")
    g.add_edge("planner", "architect")
    g.add_edge("architect", END)

    return g.compile()
