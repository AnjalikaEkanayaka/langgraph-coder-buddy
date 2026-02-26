from app.graph import build_graph
import json
import os
import re

def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "project"

def main():
    graph = build_graph()

    user_request = input("What do you want to build? ").strip()
    project_name = slugify(user_request)[:40]
    output_dir = os.path.join("generated", project_name)

    initial_state = {
        "user_request": user_request,
        "output_dir": output_dir,
        "created_files": [],
        "current_task_index": 0
    }

    final_state = graph.invoke(initial_state)

    print("\n========================")
    print("OUTPUT FOLDER")
    print("========================")
    print(output_dir)

    print("\n========================")
    print("FILES CREATED")
    print("========================")
    for f in (final_state.get("created_files") or []):
        print("-", f)

    if final_state.get("error"):
        print("\nERROR:", final_state["error"])

    print("\nDone.")

if __name__ == "__main__":
    main()