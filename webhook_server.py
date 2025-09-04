import os
import sqlite3
import threading
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -------------------------------
# Environment Variables
# -------------------------------
TOKEN = os.environ.get("TG_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TG_BOT_TOKEN non trovato!")

DB_FILE = os.environ.get("DB_FILE", "users.db")
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")

# -------------------------------
# Database
# -------------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

# Creazione tabella schedine se non esiste
with db_lock:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticket_data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Telegram Bot
# -------------------------------
application = ApplicationBuilder().token(TOKEN).build()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Benvenuto nel bot delle schedine.")

application.add_handler(CommandHandler("start", start))

# -------------------------------
# Utility schedine
# -------------------------------
def clean_old_tickets():
    """Cancella schedine più vecchie di 10 giorni."""
    limit_date = datetime.utcnow() - timedelta(days=10)
    with db_lock:
        cursor.execute("DELETE FROM tickets WHERE created_at < ?", (limit_date,))
        conn.commit()

def add_ticket(user_id: int, ticket_data: str):
    """Aggiunge una nuova schedina per un utente."""
    clean_old_tickets()
    with db_lock:
        cursor.execute("INSERT INTO tickets (user_id, ticket_data) VALUES (?, ?)",
                       (user_id, ticket_data))
        conn.commit()

def get_user_tickets(user_id: int):
    """Restituisce tutte le schedine dell'utente (max 10 giorni)."""
    clean_old_tickets()
    with db_lock:
        cursor.execute("SELECT id, ticket_data, created_at FROM tickets WHERE user_id = ?", (user_id,))
        return cursor.fetchall()

# -------------------------------
# Route webhook Telegram
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"

# -------------------------------
# Route di test (facoltativa)
# -------------------------------
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "ok"})

# -------------------------------
# Start Flask server
# -------------------------------
if __name__ == "__main__":
    application.bot.set_webhook(WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
