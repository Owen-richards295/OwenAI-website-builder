import os
from route.safe_path import resolve_safe_path

BUILD_DIR = os.path.abspath("generated_sites")
async def create_file(project_name, path, content):
    # sandbox: everything lives under generated_sites/<project_name>/
    safe_project = "".join(c for c in project_name if c.isalnum() or c in "-_") or "untitled"
    project_dir = os.path.join(BUILD_DIR, safe_project)
    full_path = os.path.abspath(os.path.join(project_dir, path))

    # block path traversal and anything escaping the sandbox
    if not full_path.startswith(os.path.abspath(project_dir)):
        return f"Blocked: '{path}' tried to write outside the project folder."

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"File written to {os.path.relpath(full_path, BUILD_DIR)} ({len(content)} chars)" 
