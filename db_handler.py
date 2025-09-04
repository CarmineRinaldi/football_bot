import sqlite3
import threading
import os

DB_FILE = os.environ.get("DB_FILE", "users.db")

class DBHandler:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self.create_table()

    def create_table(self):
        with self.lock:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, vip INTEGER DEFAULT 0, free_matches INTEGER DEFAULT 0)"
            )
            self.conn.commit()

    def get_status(self, chat_id):
        with self.lock:
            self.cursor.execute("SELECT vip, free_matches FROM users WHERE chat_id=?", (chat_id,))
            row = self.cursor.fetchone()
            if row:
                vip, free_matches = row
                return f"VIP: {bool(vip)}, Partite gratuite usate: {free_matches}"
            else:
                return "Utente non registrato."

    def add_user(self, chat_id):
        with self.lock:
            self.cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
            self.conn.commit()

    def set_vip(self, chat_id):
        with self.lock:
            self.cursor.execute("UPDATE users SET vip=1 WHERE chat_id=?", (chat_id,))
            self.conn.commit()

    def increment_free(self, chat_id):
        with self.lock:
            self.cursor.execute("UPDATE users SET free_matches = free_matches + 1 WHERE chat_id=?", (chat_id,))
            self.conn.commit()
