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
            is_vip INTEGER DEFAULT 0,
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
    await update.message.reply_text(
        "Ciao! Benvenuto nel bot delle schedine.\n"
        "Usa /aggiungischedina per aggiungere una schedina\n"
        "Usa /mieschedine per vedere le tue schedine"
    )

application.add_handler(CommandHandler("start", start))

# -------------------------------
# Utility schedine
# -------------------------------
def clean_old_tickets():
    limit_date = datetime.utcnow() - timedelta(days=10)
    with db_lock:
        cursor.execute("DELETE FROM tickets WHERE created_at < ?", (limit_date,))
        conn.commit()

def add_ticket(user_id: int, ticket_data: str, is_vip: bool):
    clean_old_tickets()
    max_matches = VIP_MAX_MATCHES if is_vip else FREE_MAX_MATCHES
    # Controllo limite
    with db_lock:
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE user_id=? AND is_vip=?", (user_id, int(is_vip)))
        count = cursor.fetchone()[0]
        if count >= max_matches:
            return False
        cursor.execute(
            "INSERT INTO tickets (user_id, ticket_data, is_vip) VALUES (?, ?, ?)",
            (user_id, ticket_data, int(is_vip))
        )
        conn.commit()
    return True

def get_user_tickets(user_id: int):
    clean_old_tickets()
    with db_lock:
        cursor.execute("SELECT id, ticket_data, is_vip, created_at FROM tickets WHERE user_id=?", (user_id,))
        return cursor.fetchall()

# -------------------------------
# Comandi Telegram schedine
# -------------------------------
async def aggiungi_schedina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("Usa /aggiungischedina <dati_schedina>")
        return
    ticket_data = " ".join(context.args)
    is_vip = False  # Qui puoi implementare controllo VIP reale se vuoi
    success = add_ticket(user_id, ticket_data, is_vip)
    if success:
        await update.message.reply_text("Schedina aggiunta correttamente!")
    else:
        await update.message.reply_text(
            f"Hai raggiunto il limite massimo di schedine ({VIP_MAX_MATCHES if is_vip else FREE_MAX_MATCHES})"
        )

async def mie_schedine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    tickets = get_user_tickets(user_id)
    if not tickets:
        await update.message.reply_text("Non hai schedine salvate.")
        return
    msg = "Le tue schedine:\n\n"
    for t in tickets:
        tipo = "VIP" if t[2] else "FREE"
        msg += f"{t[1]} ({tipo}) - {t[3]}\n"
    await update.message.reply_text(msg)

application.add_handler(CommandHandler("aggiungischedina", aggiungi_schedina))
application.add_handler(CommandHandler("mieschedine", mie_schedine))

# -------------------------------
# Route webhook Telegram
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK"

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "ok"})

# -------------------------------
# Start Flask server
# -------------------------------
if __name__ == "__main__":
    application.bot.set_webhook(WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
