from app.graph import build_graph
import json

def main():
    graph = build_graph()

    user_request = input("What do you want to build? ").strip()

    initial_state = {"user_request": user_request}
    final_state = graph.invoke(initial_state)

    print("\n========================")
    print("PLAN")
    print("========================")
    print(final_state.get("plan", ""))

    print("\n========================")
    print("TASKS (from Architect)")
    print("========================")
    tasks = final_state.get("tasks") or []
    print(json.dumps(tasks, indent=2))

    if final_state.get("error"):
        print("\nERROR:", final_state["error"])

if __name__ == "__main__":
    main()
