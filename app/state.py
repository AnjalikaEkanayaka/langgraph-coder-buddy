from typing import TypedDict, Optional, List, Dict, Any

class GraphState(TypedDict, total=False):
    # User request (input)
    user_request: str

    # Output from the planner (we’ll keep as text for now)
    plan: str

    # Architect output: List of tasks (each task = one file to generate)
    tasks: List[Dict[str, Any]]

    # For tracking which task is currently being worked on Later
    current_task_index: int

    # Debug / status info
    error: Optional[str]
