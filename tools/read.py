async def read_file(project_name, path):
	full_path = resolve_safe_path(project_name, path)
	if not os.path.exists(full_path):
		return f"No such directory exist named {project}"

	with open(full_path, "r", encoding="utf-8") as f:
		web = f.read()
		return web
