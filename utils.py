import sqlite3
import os
from datetime import datetime, timedelta

DB = os.getenv("DATABASE_URL", "users.db")

def add_ticket(user_id: int, ticket: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, ticket) VALUES (?,?)", (user_id, ticket))
    conn.commit()
    conn.close()

def get_tickets(user_id: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    cutoff = datetime.utcnow() - timedelta(hours=48)
    c.execute("SELECT ticket FROM tickets WHERE user_id=? AND created_at>=?", (user_id, cutoff))
    results = [row[0] for row in c.fetchall()]
    conn.close()
    return results
