from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.agents.planner import planner_node

def build_graph():
    g = StateGraph(GraphState)

    # Add a node named "planner"
    g.add_node("planner", planner_node)

    # Define flow: start -> planner -> end
    g.set_entry_point("planner")
    g.add_edge("planner", END)

    return g.compile()
