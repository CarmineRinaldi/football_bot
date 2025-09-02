import sqlite3
import os

DB_FILE = os.environ.get("DB_FILE", "users.db")

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("SELECT * FROM users")
rows = c.fetchall()
conn.close()

print("Utenti nel DB:")
for r in rows:
    print(r)
