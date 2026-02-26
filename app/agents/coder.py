from app.llm import get_llm
from app.tools.file_tools import write_text_file

def coder_node(state):
    tasks = state.get("tasks") or []
    idx = int(state.get("current_task_index") or 0)

    if idx >= len(tasks):
        # Nothing to do
        return state

    task = tasks[idx]
    file_path = (task.get("file_path") or "").strip()

    # If the architect ever gives "images/" or a folder, skip it for now
    if not file_path or file_path.endswith("/"):
        state["current_task_index"] = idx + 1
        return state

    purpose = (task.get("purpose") or "").strip()
    reqs = task.get("requirements") or []

    output_dir = state.get("output_dir") or "generated/demo_project"
    if state.get("created_files") is None:
        state["created_files"] = []

    # Use more tokens for code generation (but still per-file, so controlled)
    llm = get_llm(max_tokens=2500, temperature=0.2)

    requirements_text = ""
    for r in reqs:
        requirements_text += "- " + str(r) + "\n"

    prompt = f"""
You are a senior developer.

Write the COMPLETE content for this file.

FILE PATH:
{file_path}

PURPOSE:
{purpose}

REQUIREMENTS:
{requirements_text}

RULES:
- Output ONLY the file content. No markdown. No ``` fences. No explanation.
- Keep it simple and working.
- If this is HTML: link styles.css and script.js correctly.
- If this is CSS: style a clean simple UI.
- If this is JS: implement add/remove/complete tasks using DOM.
"""

    try:
        resp = llm.invoke(prompt)
        content = (resp.content or "").strip()

        # Remove markdown fences if model adds them
        if "```" in content:
            content = content.replace("```html", "").replace("```css", "").replace("```js", "")
            content = content.replace("```", "").strip()

        full_path = write_text_file(output_dir, file_path, content)

        state["created_files"].append(file_path)
        state["current_task_index"] = idx + 1
        state["error"] = None

        print(f"[Coder] Wrote: {file_path}")

    except Exception as ex:
        state["error"] = "Coder failed: " + str(ex)

    return state