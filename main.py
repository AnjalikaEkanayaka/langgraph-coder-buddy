from app.graph import build_graph
from app.llm import get_llm
import json
import os
import re
import webbrowser

def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "project"

def generate_project_name(user_request):
    try:
        llm = get_llm(max_tokens=50, temperature=0.7)
        prompt = f"""
Generate a short, cool project name for this app: "{user_request}"

RULES:
- Max 3 words
- No special characters or spaces (use underscores)
- Lowercase only
- Make it relevant and catchy
- Do NOT include words like "app", "project", "tool"
- Examples: "task_flow", "quick_notes", "budget_lens"

Return ONLY the name. Nothing else.
"""
        resp = llm.invoke(prompt)
        raw = (resp.content or "").strip()
        name = slugify(raw.split("\n")[0])[:30]
        if len(name) < 3:
            return slugify(user_request)[:30]
        return name
    except Exception:
        return slugify(user_request)[:30]


def preview_plan(user_request):
    """
    Run ONLY the planner to get a plan preview.
    We do this BEFORE running the full pipeline
    so the user can confirm before spending API calls.
    """
    from app.agents.planner import planner_node

    # Run just the planner node directly
    temp_state = {
        "user_request": user_request,
        "plan": "",
        "error": None
    }
    result = planner_node(temp_state)
    return (result.get("plan") or "").strip()


def confirm_with_user(project_name, plan):
    """
    Show the plan preview and ask user to confirm.
    Returns True if user wants to proceed, False to cancel.
    """
    print(f"\n[Namer] Project name: {project_name}")
    print("\n--- PLAN PREVIEW ---")

    # Show a trimmed version — first 800 chars is enough to get the idea
    preview = plan[:800]
    if len(plan) > 800:
        preview += "\n... (truncated)"
    print(preview)
    print("--------------------")

    while True:
        answer = input("\nProceed? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            # Keep asking if they type something random
            print("Please type y or n.")


def open_in_browser(output_dir):
    """
    Find index.html in the output folder and open it in the browser.
    """
    index_path = os.path.join(output_dir, "index.html")

    if os.path.exists(index_path):
        abs_path = os.path.abspath(index_path)
        url = "file:///" + abs_path.replace("\\", "/")  # fix Windows paths
        print(f"\n[Browser] Opening: {url}")
        webbrowser.open(url)
    else:
        print("\n[Browser] index.html not found — skipping auto-open.")


def main():
    user_request = input("What do you want to build? ").strip()
    if not user_request:
        print("No input given. Exiting.")
        return

    # ── Step 1: Generate a cool project name ────────────────────────────
    print("\n[Namer] Generating project name...")
    project_name = generate_project_name(user_request)

    # ── Step 2: Run planner and show preview ────────────────────────────
    plan = preview_plan(user_request)
    if not plan:
        print("[Error] Planner failed to generate a plan. Exiting.")
        return

    # ── Step 3: Ask user to confirm ─────────────────────────────────────
    should_proceed = confirm_with_user(project_name, plan)
    if not should_proceed:
        print("\nCancelled. No files were generated.")
        return

    # ── Step 4: Run the full pipeline ───────────────────────────────────
    print("\n[Pipeline] Starting full generation...\n")
    output_dir = os.path.join("generated", project_name)

    graph = build_graph()
    initial_state = {
        "user_request": user_request,
        "plan": plan,           # ← reuse the plan we already generated
        "output_dir": output_dir,
        "created_files": [],
        "current_task_index": 0,
        "fix_file_path": "",
        "fix_reason": "",
        "fix_attempts": 0
    }

    final_state = graph.invoke(initial_state)

    # ── Step 5: Print summary ────────────────────────────────────────────
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

    # ── Step 6: Auto open in browser ─────────────────────────────────────
    open_in_browser(output_dir)

    print("\nDone.")

if __name__ == "__main__":
    main()