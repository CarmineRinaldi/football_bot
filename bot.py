import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext, Dispatcher
import requests
import stripe
import sqlite3

# -------------------------
# VARIABILI D'AMBIENTE
# -------------------------
TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
ADMIN_HTTP_TOKEN = os.getenv("ADMIN_HTTP_TOKEN")

# -------------------------
# SETUP STRIPE
# -------------------------
stripe.api_key = STRIPE_SECRET_KEY

# -------------------------
# INIZIALIZZAZIONE FLASK
# -------------------------
app = Flask(__name__)

# -------------------------
# INIZIALIZZAZIONE BOT
# -------------------------
bot = Bot(token=TOKEN)
application = ApplicationBuilder().bot(bot).build()
dispatcher: Dispatcher = application.dispatcher

# -------------------------
# FUNZIONI UTILI
# -------------------------
def init_db():
    """Inizializza database se non esiste."""
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            is_vip INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

# -------------------------
# HANDLER COMANDI
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    await update.message.reply_text("Ciao! Bot attivo tramite webhook!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandi disponibili:\n/start - Avvia il bot\n/help - Mostra questo messaggio")

# Aggiungi qui eventuali altri comandi personalizzati
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))

# -------------------------
# ROUTE FLASK PER WEBHOOK
# -------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Riceve aggiornamenti da Telegram via webhook."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# -------------------------
# SETUP WEBHOOK ALL'AVVIO
# -------------------------
@app.before_first_request
def set_webhook():
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# -------------------------
# AVVIO SERVER FLASK
# -------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT)
