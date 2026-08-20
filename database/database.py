import sqlite3

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
