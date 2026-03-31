from app.llm import get_llm
from app.tools.file_tools import write_text_file, read_text_file

def coder_node(state):
    tasks = state.get("tasks") or []
    idx = int(state.get("current_task_index") or 0)

    fix_file_path = (state.get("fix_file_path") or "").strip()
    fix_reason = (state.get("fix_reason") or "").strip()
    fix_attempts = int(state.get("fix_attempts") or 0)

    if fix_file_path and fix_attempts >= 2:
        state["error"] = "Too many fix attempts for " + fix_file_path
        return state

    output_dir = state.get("output_dir") or "generated/demo_project"
    if state.get("created_files") is None:
        state["created_files"] = []

    if fix_file_path:
        file_path = fix_file_path
        purpose = "Fix this file based on reviewer feedback."
        reqs = []
        print("[Coder] Generating:", file_path, "(fix mode)")
    else:
        if idx >= len(tasks):
            return state

        task = tasks[idx]
        file_path = (task.get("file_path") or "").strip()

        if not file_path or file_path.endswith("/"):
            state["current_task_index"] = idx + 1
            return state

        purpose = (task.get("purpose") or "").strip()
        reqs = task.get("requirements") or []
        print("[Coder] Generating:", file_path)

    # ── FIX 1: read already-created files and inject as context ─────────
    # This is the core fix. When writing styles.css or script.js,
    # the coder can SEE the HTML that was already written.
    # This forces ID/class names to match across files.
    context_block = ""
    created = state.get("created_files") or []
    for cf in created:
        if cf == file_path:
            continue  # don't inject the file we're about to overwrite
        try:
            existing = read_text_file(output_dir, cf)
            if existing and existing.strip():
                context_block += f"\n--- ALREADY GENERATED: {cf} ---\n{existing}\n"
        except:
            pass

    if context_block:
        context_intro = (
            "IMPORTANT: The following files have already been generated. "
            "Your output MUST use the same IDs, class names, and structure. "
            "Do NOT invent new IDs or classes.\n"
            + context_block
        )
    else:
        context_intro = ""

    llm = get_llm(max_tokens=2500, temperature=0.2)

    # ── FIX 2: tighter file-type rules ──────────────────────────────────
    if file_path.endswith(".html"):
        file_rules = (
            "Output ONLY HTML.\n"
            "Do NOT include any <style> blocks.\n"
            "Do NOT include any inline <script> blocks.\n"
            "Link styles.css in <head> and script.js at end of <body>.\n"
            "Use simple clear IDs like: task-input, add-btn, task-list.\n"
        )
    elif file_path.endswith(".css"):
        file_rules = (
            "Output ONLY CSS.\n"
            "Do NOT include any HTML tags.\n"
            "Do NOT include any JavaScript.\n"
            "Style only the elements and classes that exist in index.html.\n"
            "Make the UI look modern and clean:\n"
            "- Use a nice color scheme (not just black and white)\n"
            "- Add padding, margins, border-radius, box-shadow\n"
            "- Center the app on the page\n"
            "- Make buttons look clickable with hover effects\n"
            "- Use a clean font like Arial or system-ui\n"
            "- Make it mobile friendly\n"
        )
    elif file_path.endswith(".js"):
        file_rules = (
            "Output ONLY JavaScript.\n"
            "Do NOT include any HTML or CSS.\n"
            "Use ONLY the IDs and class names that exist in index.html.\n"
            "Implement all functionality described in the PURPOSE above.\n"
            "Use localStorage to persist data across page refreshes.\n"
            "No external libraries. Pure vanilla JS only.\n"
        )
    else:
        file_rules = "Output only the content for this file type."

    requirements_text = "\n".join(f"- {r}" for r in reqs)

    # ── FIX 3: context injected into prompt ──────────────────────────────
    user_request = (state.get("user_request") or "a web app").strip()

    prompt = f"""
    You are a senior developer writing one file for this project: {user_request}

FILE TO WRITE:
{file_path}

PURPOSE:
{purpose}

REQUIREMENTS:
{requirements_text}

REVIEWER FIX NOTE (if any):
{fix_reason}

{context_intro}

RULES (must follow strictly):
{file_rules}

FINAL RULES:
- Output ONLY the raw file content. No markdown. No ``` fences. No explanation.
- Keep it simple and working.
- Every ID and class name must match exactly across all files.
"""

    try:
        resp = llm.invoke(prompt)
        content = (resp.content or "").strip()

        # Remove markdown fences if model adds them
        if "```" in content:
            content = content.replace("```html", "").replace("```css", "")
            content = content.replace("```js", "").replace("```javascript", "")
            content = content.replace("```", "").strip()

        full_path = write_text_file(output_dir, file_path, content)
        state["created_files"].append(file_path)

        if fix_file_path:
            state["fix_attempts"] = fix_attempts + 1
            state["fix_file_path"] = ""
            state["fix_reason"] = ""
        else:
            state["fix_attempts"] = 0
            state["current_task_index"] = idx + 1

        state["error"] = None
        print(f"[Coder] Wrote: {file_path}")

    except Exception as ex:
        state["error"] = "Coder failed: " + str(ex)

    return state