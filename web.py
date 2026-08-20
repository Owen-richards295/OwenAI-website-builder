#STEPS TO FOLLOW IN BUILDING THE WEB BUILDER HTML, CSS, JAVASCRIPT.

#1. after getting instruction to build a website from a chat interface
#2. It uses the first tool, which is to create a file  and start writing inside it
#3. then it uses playwright tool to open the website ith the file path
#4. then it uses playwright again to screenshot the page and see if theres any error in the css andd layout


from flask import Flask, url_for, redirect, request, render_template, flash, session
from openai import AsyncOpenAI
import asyncio
from tools.create import create_file
from tools.read import read_file
from tools.edit import edit_file
from route.reference import load_reference
from route.safe_path import resolve_safe_path
from database.database import init_db
from route.trim import trim_history
from dotenv import load_dotenv
from tools.tool import tool
import os
from ai_workflow.intelligence import intelligence
import json
import sqlite3
from playwright.async_api import async_playwright


load_dotenv("hide.env")
app = Flask(__name__)
DB_PATH = "memory.db"




@app.route("/", methods=["POST", "GET"])
async def home():
	return await intelligence()
	

if __name__ == "__main__":
	app.run(debug=True, port=5009, host="0.0.0.0")












