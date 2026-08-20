tool = [{"type": "function",
"function": {
    "name": "create_file",
    "description": "Creates or overwrites a file inside the current project's own folder. Always give the project a clear, consistent name across calls for the same build.",
    "parameters": {"type": "object",
        "properties": {
            "project_name": {"type": "string", "description": "Short slug for this build, e.g. 'portfolio-site'. Use the same name for every file in the same project."},
            "path": {"type": "string", "description": "File path relative to the project folder, e.g. 'index.html' or 'css/style.css'"},
            "content": {"type": "string", "description": "The full HTML/CSS/JS content to write into the file"}
        },
        "required": ["project_name", "path", "content"]}}
},
{"type": "function",
"function": {
    "name": "edit_file",
    "description": "Makes a targeted change to an existing file by replacing one exact snippet with another — it does NOT rewrite the whole file. old_str must be copied verbatim from the file's current content (use read_file first) and must be unique enough to match only one location; include a few surrounding lines if the text could appear more than once. Use this for fixes and small changes. Use create_file only when writing a brand-new file or intentionally replacing its entire contents.",
    "parameters": {"type": "object",
        "properties": {
            "project_name": {"type": "string", "description": "Short slug for this build, e.g. 'portfolio-site'. Use the same name for every file in the same project."},
            "path": {"type": "string", "description": "File path relative to the project folder, e.g. 'index.html', 'css/style.css' or script/script.js"},
            "old_str": {"type": "string", "description": "The exact existing text to replace, copied verbatim from the file (via read_file). Must match exactly once — include enough surrounding context to make it unique."},
            "new_str": {"type": "string", "description": "The replacement text that will take old_str's place."}
        },
        "required": ["project_name", "path", "old_str", "new_str"]}}
},
{"type": "function",
"function": {
    "name": "read_file",
    "description": "Reads and returns the current contents of a file in the project. Always call this before edit_file, so you have the exact current text to copy old_str from — never guess or reconstruct file contents from memory.",
    "parameters": {"type": "object",
        "properties": {
            "project_name": {"type": "string", "description": "Short slug for this build, matching the project_name used when the file was created."},
            "path": {"type": "string", "description": "File path relative to the project folder, e.g. 'index.html', 'css/style.css', or 'script/script.js'"}
        },
        "required": ["project_name", "path"]}}
},]
