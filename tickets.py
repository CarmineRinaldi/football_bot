import sqlite3
import os
import json
from datetime import date

DB_FILE = os.environ.get("DB_FILE", "users.db")  # stesso DB di users

def init_tickets_db():
    """Crea la tabella tickets se non esiste."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pronostici TEXT,
            vip_only INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_ticket(user_id, pronostici, vip_only=0):
    """Salva una schedina per un utente."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (user_id, pronostici, vip_only, created_at) VALUES (?, ?, ?, ?)",
        (user_id, json.dumps(pronostici), vip_only, date.today().isoformat())
    )
    conn.commit()
    conn.close()

def get_tickets(user_id, is_vip=0):
    """Recupera le schedine per l'utente (VIP o Free)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if is_vip:
        c.execute(
            "SELECT ticket_id, pronostici FROM tickets WHERE user_id=? ORDER BY ticket_id DESC",
            (user_id,)
        )
    else:
        # solo schedine non VIP, max 10
        c.execute(
            "SELECT ticket_id, pronostici FROM tickets WHERE user_id=? AND vip_only=0 ORDER BY ticket_id DESC LIMIT 10",
            (user_id,)
        )
    rows = c.fetchall()
    conn.close()
    tickets = []
    for r in rows:
        tickets.append({
            "ticket_id": r[0],
            "pronostici": json.loads(r[1])
        })
    return tickets

def delete_old_tickets():
    """Opzionale: pulisce schedine di giorni precedenti."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("DELETE FROM tickets WHERE created_at<>?", (today,))
    conn.commit()
    conn.close()
