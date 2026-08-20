import asyncio
from flask import Flask, url_for, redirect, request, render_template, flash, session
import sqlite3
from openai import AsyncOpenAI
from route.reference import REFERENCE_DESIGN 
from route.safe_path import resolve_safe_path
from route.prompt import prompts
from tools.create import create_file
from tools.read import read_file
from tools.edit import edit_file
import json
from tools.tool import tool
from route.trim import trim_history
import os




GEMINI_API = os.getenv("GEMINI_API")
DB_PATH = "memory.db"


async def intelligence():
	if request.method == "POST":
		content = request.form.get("content", "").strip()
		print("User: ", content)
		conn = sqlite3.connect(DB_PATH)
		cursor = conn.cursor()
		message = cursor.execute("SELECT user_message, ai_reply FROM memoir ORDER BY id DESC LIMIT 100").fetchall()
		message = list(reversed(message))
		conn.close()

		client = AsyncOpenAI(
			api_key=GEMINI_API,
			base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

		try:
			messages_ai = [{"role": "system", "content": prompts}]

			for user_message, ai_reply in message:
				messages_ai.append({"role": "user", "content": content})
				messages_ai.append({"role": "assistant", "content": ai_reply})

			messages_ai.append({"role": "user", "content": f"Reference style (for inspiration only, don't copy): {REFERENCE_DESIGN[:2000]}\n\nBuild: {content}"})
			

			while True:
				messages_ai = trim_history(messages_ai)
				response = await client.chat.completions.create(
					model="gemini-2.5-flash",
					messages=messages_ai,
					tools = tool,
					tool_choice = "auto",
					temperature=0.4,
					max_tokens=8000
					)

				ai_reply = response.choices[0].message
				print("FINISH REASON:", response.choices[0].finish_reason)
				print("RAW CONTENT:", repr(ai_reply.content))
				print("RAW TOOL CALLS:", ai_reply.tool_calls)

				if not ai_reply.tool_calls:
					ai_reply = ai_reply.content or "ERROR CREATING FILE"
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
