# check_db.py
import sqlite3
import os

DB_FILE = os.environ.get("DB_FILE", "users.db")

def show_users():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database {DB_FILE} non trovato.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, is_vip FROM users")
    rows = c.fetchall()
    conn.close()

    if rows:
        print("📋 Utenti registrati nel DB:")
        for r in rows:
            print(f"ID: {r[0]} | Username: {r[1]} | VIP: {r[2]}")
    else:
        print("⚠️ Nessun utente trovato nel DB.")

if __name__ == "__main__":
    show_users()
