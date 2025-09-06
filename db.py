import sqlite3
import os

DATABASE_URL = os.getenv("DATABASE_URL", "users.db")
conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()

# Tabelle utenti e ticket
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    plan TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    league TEXT,
    matches TEXT
)
''')
conn.commit()

# Funzioni DB
def add_user(user_id: int, plan: str):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, plan) VALUES (?, ?)", (user_id, plan))
    conn.commit()

def get_user_plan(user_id: int):
    cursor.execute("SELECT plan FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def add_ticket(user_id: int, league: str, matches: list):
    matches_str = ",".join(matches)
    cursor.execute("INSERT INTO tickets (user_id, league, matches) VALUES (?, ?, ?)", (user_id, league, matches_str))
    conn.commit()

def get_user_tickets(user_id: int):
    cursor.execute("SELECT ticket_id, league, matches FROM tickets WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    tickets = []
    for row in rows:
        tickets.append({
            "ticket_id": row[0],
            "league": row[1],
            "matches": row[2].split(",")
        })
    return tickets
