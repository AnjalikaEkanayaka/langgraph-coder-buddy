import re
from app.tools.file_tools import read_text_file

def _contains_any(text, parts):
    t = text.lower()
    for p in parts:
        if p.lower() in t:
            return True
    return False

def reviewer_node(state):
    print("[Reviewer] Checking last written file...")

    output_dir = state.get("output_dir") or ""
    created = state.get("created_files") or []
    if not output_dir or not created:
        return state

    last_file = created[-1]
    content = read_text_file(output_dir, last_file)

    # ── FIX 1: empty file check ─────────────────────────────────────────
    if not content or not content.strip():
        state["fix_file_path"] = last_file
        state["fix_reason"] = "File is empty or blank."
        print("[Reviewer] Fix requested:", last_file, "| Reason: empty file")
        return state

    # ── FIX 2: skip non-web files ───────────────────────────────────────
    allowed_files = {"index.html", "styles.css", "script.js"}
    if last_file not in allowed_files:
        print(f"[Reviewer] Skipping non-web file: {last_file}")
        state["fix_file_path"] = ""
        state["fix_reason"] = ""
        return state

    # ── HTML checks ─────────────────────────────────────────────────────
    if last_file == "index.html":
        issues = []

        if "<html" not in content.lower():
            issues.append("Missing <html> tag.")
        if "<body" not in content.lower():
            issues.append("Missing <body> tag.")
        if "styles.css" not in content:
            issues.append("Missing link to styles.css.")
        if "script.js" not in content:
            issues.append("Missing link to script.js.")
        if "<style" in content.lower():
            issues.append("Has inline <style> block. Move CSS to styles.css.")

        # Check for inline script blocks (allow src= links, flag inline code)
        inline_scripts = re.findall(
            r'<script(?![^>]*src)[^>]*>(.+?)</script>',
            content, re.DOTALL | re.IGNORECASE
        )
        if any(s.strip() for s in inline_scripts):
            issues.append("Has inline <script> block. Move JS to script.js.")

        if issues:
            state["fix_file_path"] = last_file
            state["fix_reason"] = "HTML issues: " + " | ".join(issues)
            print("[Reviewer] Fix requested:", last_file, "|", state["fix_reason"])
            return state

    # ── CSS checks ──────────────────────────────────────────────────────
    if last_file == "styles.css":
        issues = []

        if _contains_any(content, ["<html", "<!doctype", "<body", "<div", "<head"]):
            issues.append("CSS file contains HTML tags.")
        if _contains_any(content, ["function ", "const ", "let ", "var ", "document.", "addEventListener"]):
            issues.append("CSS file contains JavaScript.")
        if "{" not in content or "}" not in content:
            issues.append("CSS file has no valid rules (missing { }).")

        if issues:
            state["fix_file_path"] = last_file
            state["fix_reason"] = "CSS issues: " + " | ".join(issues)
            print("[Reviewer] Fix requested:", last_file, "|", state["fix_reason"])
            return state

    # ── JS checks ───────────────────────────────────────────────────────
    if last_file == "script.js":
        issues = []

        if _contains_any(content, ["<html", "<!doctype", "<body"]):
            issues.append("JS file contains HTML structure tags.")
        if _contains_any(content, ["body {", ".container {", "margin:", "padding:", "color:"]):
            issues.append("JS file contains CSS rules.")
        if not _contains_any(content, ["function", "const ", "let ", "var ", "=>"]):
            issues.append("JS file has no JavaScript code.")
        if not _contains_any(content, ["document.", "getElementById", "querySelector", "addEventListener"]):
            issues.append("JS has no DOM interaction.")

        # ── NEW: cross-check JS classList against styles.css ────────────
        # This catches the "Complete button does nothing" bug.
        # If JS toggles a class, that class MUST exist in styles.css.
        if "classList" in content or "className" in content:
            try:
                css_content = read_text_file(output_dir, "styles.css")
                if css_content:
                    # Find all class names used in classList operations
                    js_classes = re.findall(
                        r'classList\.\w+\(["\'](\w[\w-]*)["\']',
                        content
                    )
                    missing_classes = []
                    for cls in js_classes:
                        if f".{cls}" not in css_content:
                            missing_classes.append(cls)

                    if missing_classes:
                        issues.append(
                            f"JS uses CSS class(es) {missing_classes} "
                            f"but they are not defined in styles.css. "
                            f"Add styles for these classes."
                        )
            except Exception:
                pass  # styles.css not readable yet, skip cross-check

        # ── NEW: cross-check JS IDs against index.html ──────────────────
        # If JS does getElementById('foo'), index.html must have id="foo".
        try:
            html_content = read_text_file(output_dir, "index.html")
            if html_content:
                # Find all IDs accessed in JS
                js_ids = re.findall(
                    r'getElementById\(["\'](\w[\w-]*)["\']',
                    content
                )
                missing_ids = []
                for id_ in js_ids:
                    if f'id="{id_}"' not in html_content and f"id='{id_}'" not in html_content:
                        missing_ids.append(id_)

                if missing_ids:
                    issues.append(
                        f"JS uses getElementById for {missing_ids} "
                        f"but these IDs are missing from index.html. "
                        f"Add matching id attributes."
                    )
        except Exception:
            pass  # index.html not readable yet, skip cross-check

        if issues:
            state["fix_file_path"] = last_file
            state["fix_reason"] = "JS issues: " + " | ".join(issues)
            print("[Reviewer] Fix requested:", last_file, "|", state["fix_reason"])
            return state

    # ── All checks passed ───────────────────────────────────────────────
    state["fix_file_path"] = ""
    state["fix_reason"] = ""
    print("[Reviewer] OK:", last_file)
    return state