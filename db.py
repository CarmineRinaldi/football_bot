# db.py
import sqlite3
import os

# Percorso del database (di default users.db, oppure preso da variabile ambiente)
DB_FILE = os.environ.get("DB_FILE", "users.db")

def init_db():
    """Crea le tabelle users e tickets se non esistono già."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Tabella utenti
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    is_vip INTEGER DEFAULT 0
                )''')
    
    # Tabella schedine / pronostici assegnati agli utenti
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    ticket_data TEXT,
                    visible_count INTEGER DEFAULT 3,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )''')
    
    conn.commit()
    conn.close()

# ==========================
# Funzioni utente
# ==========================
def add_user(user_id, username):
    """Aggiunge un nuovo utente al DB (se non esiste già)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def set_vip(user_id, vip=1):
    """Imposta un utente come VIP (1) o non VIP (0)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_vip=? WHERE user_id=?", (vip, user_id))
    conn.commit()
    conn.close()

def is_vip(user_id):
    """Ritorna True se l'utente è VIP."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_vip FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1

def get_all_users():
    """Ritorna la lista di tutti gli user_id registrati."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# ==========================
# Funzioni schedine / pronostici
# ==========================
def add_ticket(user_id, ticket_data, visible_count=3):
    """Aggiunge una nuova schedina per un utente."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, ticket_data, visible_count) VALUES (?, ?, ?)",
              (user_id, ticket_data, visible_count))
    conn.commit()
    conn.close()

def get_user_tickets(user_id):
    """Ritorna tutte le schedine di un utente con limitazione visibile se non VIP."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_data, visible_count FROM tickets WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    tickets = []
    for data, visible in rows:
        if is_vip(user_id):
            tickets.append(data)  # VIP vede tutto
        else:
            # Free: mostra solo i primi N pronostici
            import json
            try:
                ticket_json = json.loads(data)
                tickets.append(ticket_json[:visible])
            except Exception:
                tickets.append([])  # se json errato
    return tickets
