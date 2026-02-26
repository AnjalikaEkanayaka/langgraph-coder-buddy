import os

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def safe_join(base_dir, relative_path):
    """
    Prevent path traversal like ../../Windows/System32
    Only allow writing inside base_dir.
    """
    base_dir = os.path.abspath(base_dir)
    target_path = os.path.abspath(os.path.join(base_dir, relative_path))

    if not target_path.startswith(base_dir):
        raise ValueError("Blocked unsafe path: " + relative_path)

    return target_path

def write_text_file(base_dir, relative_path, content):
    """
    Writes a file safely inside base_dir.
    Creates folders if needed.
    """
    target_path = safe_join(base_dir, relative_path)
    parent = os.path.dirname(target_path)
    ensure_dir(parent)

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    return target_path