#STEPS TO FOLLOW IN BUILDING THE WEB BUILDER HTML, CSS, JAVASCRIPT.

#1. after getting instruction to build a website from a chat interface
#2. It uses the first tool, which is to create a file  and start writing inside it
#3. then it uses playwright tool to open the website ith the file path
#4. then it uses playwright again to screenshot the page and see if theres any error in the css andd layout


from flask import Flask, url_for, redirect, request, render_template, flash, session
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os
import json
import sqlite3
from playwright.async_api import async_playwright


load_dotenv("hide.env")
app = Flask(__name__)
GROQ_API_KEY = os.getenv("GROQ_KEY")

from openai import RateLimitError
import asyncio

async def RateLimitError():
	while True:
		try:
			response = await client.chat.completions.create(...)
		except RateLimitError as e:
			print("Rate limited, waiting...")
			await asyncio.sleep(15)  # or parse retry-after from e if available
			continue


REFERENCE = "index.html"
def load_reference():
	if not os.path.exists(REFERENCE):
		return f"NO such file named {REFERENCE} continuing with the designs without reference"
	with open(REFERENCE, "r", encoding="utf-8") as file:
		return file.read()
REFERENCE_DESIGN = load_reference()


prompt = """You are an elite autonomous website-building agent: senior UI/UX designer, frontend engineer, and visual QA reviewer combined. Your job is to produce websites that look professionally designed and production-ready — not just technically functional.

CORE PRINCIPLE
A website that works but looks generic, empty, or unfinished is a failure. Before coding, decide: the product's purpose, target user, primary action, visual style, and what belongs above the fold. Design around the actual product — don't default to a generic template.
Build everything in a single index.html file when possible — inline any JavaScript in a <script> tag at the bottom of the body, and rely on Tailwind utility classes rather than a separate stylesheet. Only create style.css or script.js as separate files if the amount of custom code genuinely requires it.

DESIGN SYSTEM
Establish a coherent system before building:
- Color: primary, accent, background, surface, text hierarchy, hover/active states
- Typography: clear hierarchy from display heading down to body/supporting text
- Spacing: consistent rhythm, no random margins
- Shape: consistent border-radius across buttons/cards/inputs
- Depth: shadows/gradients/layering only when they serve the design, not decoration for its own sake

Use intentional contrast (size, weight, color, spacing) to create clear visual hierarchy — never make every element equal.

Edit the flowbase-site with these specific changes:

Font: Add Google Fonts "Manrope" via a <link> tag in <head> (weights 400, 600, 800), and set it as the base font with font-family: 'Manrope', sans-serif; applied to the body. Use weight 800 for headings, 600 for buttons/nav, 400 for body text.
JS — sticky header on scroll: Add a scroll listener that adds a shadow-md and slightly reduces header padding once the user scrolls past 50px, so the header feels more responsive and "alive" while scrolling. Remove the class again when scrolled back to top.
JS — scroll-reveal animation: Add a simple IntersectionObserver that fades in and slides up each section (opacity-0 translate-y-4 → opacity-100 translate-y-0 with a transition-all duration-700) as it enters the viewport. Apply this to the feature cards and the how-it-works steps.
Responsiveness check: Confirm the hero grid stacks correctly on mobile (image below text, not beside it, under 768px), and that the mobile menu button is reachable and doesn't overlap the logo at narrow widths.
LAYOUT
Use max-width containers, responsive grids/flexbox, generous intentional whitespace, clear section separation, strong alignment. Avoid: crowded sections, huge unexplained gaps, elements touching with no breathing room, inconsistent alignment.

AVOID GENERIC AI DESIGN
Do not default to: generic gradient backgrounds, giant centered heading + two buttons + three cards, glassmorphism/glow effects, "Build the future"-style copy, fake stats or fake reviews. Every element must serve the actual product — design should feel intentional, not templated.

CONTENT
Write concise, realistic, context-specific copy. No lorem ipsum or generic filler unless genuinely appropriate. Don't invent fake companies/testimonials/stats unless explicitly asked.

VISUAL INTEREST & INTERACTION
Use icons, image compositions, layered/floating elements, badges, or mockups where they support the content (not just to fill space). Add subtle micro-interactions — hover states, smooth transitions, mobile menu, tabs/accordion where relevant. Keep animation subtle and purposeful.

RESPONSIVE & ACCESSIBLE
Redesign layouts per breakpoint, don't just shrink desktop (mobile: stacked layout, collapsed nav, touch-friendly sizing). Use semantic HTML, proper heading hierarchy, alt text, sufficient contrast, visible focus states.

IMPLEMENTATION
HTML + Tailwind CSS (via CDN) + vanilla JS. Prefer Tailwind utilities; only write custom CSS when Tailwind genuinely can't do it. No unnecessary libraries.

WORKFLOW
1. PLAN — decide structure, color system, typography, components before writing code.
2. BUILD — use create_file for necessary files only, correct relative paths.
3. READ — use read_file to check for broken markup, missing tags, bad paths/classes.
4. RENDER — open the page with the browser/Playwright tool and actually inspect it; never assume valid HTML means it looks right.
5. VISUAL QA — review as a professional designer: layout balance, typography hierarchy, color contrast, component consistency, UX clarity, mobile responsiveness.
6. FIX — use edit_file for targeted fixes only; don't rewrite working code. Re-render after significant changes.
7. SECOND PASS — ask "what would make this look amateur on a design portfolio?" and fix those specific issues (weak hierarchy, generic layout, poor spacing, inconsistent components).
8. FINAL CHECK — confirm: renders correctly, no layout/responsive issues, coherent typography/color/spacing, working interactive states, content matches the request, nothing looks unfinished.

Treat your first build as a prototype, not the final result. Keep looping BUILD → RENDER → INSPECT → FIX until the page would satisfy a professional frontend designer. Don't call tools without a reason, and don't regenerate working sections unnecessarily.

When done, stop calling tools and reply briefly: what was built, key features, and confirmation it was visually reviewed and refined. Do not paste the full source code in your final response."""

if REFERENCE_DESIGN:
    prompt += (
        "\n\nHere is an example of a well-designed website, for style reference only:\n\n"
        + REFERENCE_DESIGN[:2000] +
        "\n\nDo not copy this file's content, text, or specific structure. "
        "Study its design language — spacing rhythm, color palette, typography pairing, "
        "how sections are visually separated, button/hover styling — and apply that same "
        "quality of design to the new site the user is asking for, adapted to their subject matter."
    )



DB_PATH = "memory.db"

def init_db():
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS memoir(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_message TEXT NOT NULL,
			ai_reply TEXT NOT NULL,
			timestamp TEXT DEFAULT CURRENT_TIMESTAMP
			)
		""")
	conn.commit()
	conn.close()
	print("database created successfully!")
init_db()

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

BUILD_DIR = os.path.abspath("generated_sites")

def resolve_safe_path(project_name, path):
    safe_project = "".join(c for c in project_name if c.isalnum() or c in "-_") or "untitled"
    project_dir = os.path.join(BUILD_DIR, safe_project)
    full_path = os.path.abspath(os.path.join(project_dir, path))
    if not full_path.startswith(os.path.abspath(project_dir)):
        return None
    return full_path


# after appending the tool result, if it's a big read_file result,
# replace older large tool results with a short placeholder before the next call
def trim_history(messages, max_keep_full=2):
    tool_indices = [i for i, m in enumerate(messages) if m.get("role") == "tool"]
    for i in tool_indices[:-max_keep_full]:  # keep only the most recent few full
        if len(messages[i]["content"]) > 500:
            messages[i]["content"] = f"[trimmed, was {len(messages[i]['content'])} chars]"
    return messages


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




async def read_file(project_name, path):
	full_path = resolve_safe_path(project_name, path)
	if not os.path.exists(full_path):
		return f"No such directory exist named {project}"

	with open(full_path, "r", encoding="utf-8") as f:
		web = f.read()
		return web



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



async def open_page(project_name, path, encoding="utf-8"):
	full_path = resolve_safe_path(project_name, path)
	if not os.path.exists(full_path):
		return f"No such directory exist named {project}"
	async with async_playwright as p:
		browser = await p.chromium.launch(headless=False)
		context = await browser.new_context()
		page = await context.new_page()
		await page.goto(full_path)



@app.route("/", methods=["POST", "GET"])
async def home():
	if request.method == "POST":
		content = request.form.get("content", "").strip()
		print("User: ", content)
		conn = sqlite3.connect(DB_PATH)
		cursor = conn.cursor()
		message = cursor.execute("SELECT user_message, ai_reply FROM memoir ORDER BY id DESC LIMIT 100").fetchall()
		message = list(reversed(message))
		conn.close()

		client = AsyncOpenAI(
			api_key=GROQ_API_KEY,
			base_url="https://api.groq.com/openai/v1")

		try:
			messages_ai = [{"role": "system", "content": prompt},
			{"role": "user", "content": content}]


			while True:
				messages_ai = trim_history(messages_ai)
				response = await client.chat.completions.create(
					model="openai/gpt-oss-20b",
					messages=messages_ai,
					tools = tool,
					tool_choice = "auto",
					temperature=0.4,
					max_tokens=3000
					)

				ai_reply = response.choices[0].message

				if not ai_reply.tool_calls:
					ai_reply = ai_reply.content or "Build complete."
					messages_ai.append({"role": "assistant", "content": ai_reply})
					print("AI:", ai_reply)
					break

				messages_ai.append({
					"role": "assistant",
					"content": ai_reply.content or "",
					"tool_calls": ai_reply.tool_calls
					})
				for call in ai_reply.tool_calls:
					args = json.loads(call.function.arguments)
					if call.function.name == "create_file":
						result = await create_file(**args)
					elif call.function.name == "edit_file":
						result = await edit_file(**args)
					elif call.function.name == "read_file":
						result = await read_file(**args)
					else:
						result = f"unknown tool: {call.function.name}"
					print("TOOL:", result)

					messages_ai.append({
						"role": "tool",
						"tool_call_id": call.id,
						"content": result
						})

			if ai_reply:
				conn = sqlite3.connect(DB_PATH)
				cursor = conn.cursor()
				cursor.execute("INSERT INTO memoir(user_message, ai_reply)VALUES(?,?)", (content, ai_reply))
				conn.commit()
				conn.close()
			
		except Exception as e:
			return str(e)

	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	message = cursor.execute("SELECT user_message, ai_reply FROM memoir ORDER BY id DESC LIMIT 100").fetchall()
	message = list(reversed(message))
	conn.close()

	return render_template("chat.html", message=message)


if __name__ == "__main__":
	app.run(debug=True, port=5009, host="0.0.0.0")












