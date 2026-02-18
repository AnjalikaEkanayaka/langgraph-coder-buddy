from app.graph import build_graph

def main():
    graph = build_graph()

    user_request = input("What do you want to build? ").strip()

    initial_state = {"user_request": user_request}
    final_state = graph.invoke(initial_state)

    print("\n=== FINAL STATE ===")
    for k, v in final_state.items():
        print(f"\n{k}:\n{v}")

if __name__ == "__main__":
    main()
