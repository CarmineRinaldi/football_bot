import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_FILE = os.environ.get("DB_FILE", "users.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        is_vip INTEGER DEFAULT 0
                    )''')
        conn.commit()
        conn.close()
        logger.info("DB inizializzato: %s", DB_FILE)
    except Exception as e:
        logger.error("Errore init_db: %s", e)

def add_user(user_id, username):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)", (user_id, username))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Errore add_user: %s", e)

def set_vip(user_id, vip=1):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET is_vip=? WHERE user_id=?", (vip, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Errore set_vip: %s", e)

def get_all_users():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.error("Errore get_all_users: %s", e)
        return []
