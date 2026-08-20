async def edit_file(project_name, path, old_str, new_str):
	full_path = resolve_safe_path(project_name, path)
	if not os.path.exists(full_path):
		return f"No such directory exist named {project}"

	with open(full_path, "r", encoding="utf-8") as f:
		web = f.read()

	count = web.count(old_str)
	if count == 0:
		return f"Edit failed: old_str not found in {path}. Re-read the file and try again."
	if count > 1:
		return f"Edit failed: old_str appears {count} times in {path}. Make it more specific (include more surrounding text)."

	new_content = web.replace(old_str, new_str, 1)
	with open(full_path, "w", encoding="utf-8") as file:
		file.write(new_content)
	return f"Edited {path}: replaced {len(old_str)} chars with {len(new_str)} chars"
