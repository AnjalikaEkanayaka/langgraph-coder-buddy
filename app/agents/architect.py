import json
from app.llm import get_llm

def architect_node(state):
    print("[Architect] Creating file tasks (JSON)...")

    plan = (state.get("plan") or "").strip()
    if not plan:
        state["error"] = "plan is empty (planner did not produce a plan)"
        state["tasks"] = []
        return state

    # ── FIX 1: detect what kind of project the user wants ──────────────
    # We read the original user request to decide the tech stack.
    # This stops the LLM from guessing "React Native" when user said "simple".
    user_request = (state.get("user_request") or "").lower()

    if any(k in user_request for k in ["react native", "mobile", "android", "ios"]):
        stack_rule = "Use React Native. Files must be .js components."
    elif any(k in user_request for k in ["react", "next", "vue", "angular"]):
        stack_rule = "Use the requested JS framework."
    else:
        # Default: plain web — this is the most common case
        stack_rule = (
            "Use ONLY plain HTML, CSS, and JavaScript. "
            "No React. No frameworks. No Firebase. No npm. "
            "Output exactly 3 files: index.html, styles.css, script.js. "
            "Nothing else."
        )

    llm = get_llm(max_tokens=1500)

    # ── FIX 2: much stricter prompt ─────────────────────────────────────
    # Old prompt let the LLM decide the stack freely → hallucinations.
    # New prompt locks the stack based on user intent detected above.
    prompt = f"""
You are a software architect.

Convert this project plan into a minimal list of file-writing tasks.

PLAN:
{plan}

STACK RULE (follow exactly):
{stack_rule}

RULES:
- Output ONLY valid JSON. No markdown. No explanation. No comments.
- Use the MINIMUM number of files needed. Do not over-engineer.
- Each file_path must be UNIQUE. No duplicate file names.
- Do NOT include: package.json, README.md, config files, or image folders.
- Do NOT include files that require external services (Firebase, AWS, etc).

Return this EXACT format:

{{
  "tasks": [
    {{
      "file_path": "index.html",
      "purpose": "short reason why this file exists",
      "requirements": [
        "requirement 1",
        "requirement 2"
      ]
    }}
  ]
}}
"""

    try:
        resp = llm.invoke(prompt)
        text = resp.content.strip()

        print("\n--- RAW ARCHITECT OUTPUT ---")
        print(text)
        print("--- END RAW OUTPUT ---\n")

        # Clean markdown fences if model adds them
        if "```" in text:
            text = text.replace("```json", "").replace("```", "").strip()

        # Extract JSON safely
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end+1]

        data = json.loads(text)
        raw_tasks = data.get("tasks", [])

        # ── FIX 3: deduplicate tasks by file_path ───────────────────────
        # Old code had no dedup → firebase.js written 4 times.
        # We keep only the FIRST occurrence of each file_path.
        seen = set()
        unique_tasks = []
        for task in raw_tasks:
            fp = (task.get("file_path") or "").strip()
            if fp and fp not in seen:
                seen.add(fp)
                unique_tasks.append(task)
            else:
                print(f"[Architect] Skipping duplicate: {fp}")

        # ── FIX 4: enforce plain web file whitelist ─────────────────────
        # Even after dedup, the LLM might sneak in React/Firebase files.
        # If the user wanted plain web, we hard-filter to only allowed extensions.
        if "ONLY plain HTML" in stack_rule:
            allowed = {"index.html", "styles.css", "script.js"}
            filtered = [t for t in unique_tasks if t.get("file_path") in allowed]

            # If LLM returned wrong files, override completely with safe defaults
            if not filtered:
                print("[Architect] LLM ignored stack rule. Using safe defaults.")
                filtered = [
                    {"file_path": "index.html",  "purpose": "Main HTML page",   "requirements": ["structure the UI"]},
                    {"file_path": "styles.css",  "purpose": "App styling",       "requirements": ["style the UI"]},
                    {"file_path": "script.js",   "purpose": "App logic",         "requirements": ["implement functionality"]},
                ]

            unique_tasks = filtered

        state["tasks"] = unique_tasks
        state["current_task_index"] = 0
        state["error"] = None
        print(f"[Architect] Tasks count: {len(unique_tasks)}")

    except Exception as ex:
        state["tasks"] = []
        state["error"] = "Architect failed: " + str(ex)

    return state