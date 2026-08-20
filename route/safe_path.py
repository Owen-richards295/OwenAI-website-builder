import os 



BUILD_DIR = os.path.abspath("generated_sites")
def resolve_safe_path(project_name, path):
    safe_project = "".join(c for c in project_name if c.isalnum() or c in "-_") or "untitled"
    project_dir = os.path.join(BUILD_DIR, safe_project)
    full_path = os.path.abspath(os.path.join(project_dir, path))
    if not full_path.startswith(os.path.abspath(project_dir)):
        return None
    return full_path
