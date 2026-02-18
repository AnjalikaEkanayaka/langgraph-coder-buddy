from typing import TypedDict, Optional

class GraphState(TypedDict, total=False):
    # User request (input)
    user_request: str

    # Output from the planner (we’ll keep as text for now)
    plan: str

    # Debug / status info
    error: Optional[str]
