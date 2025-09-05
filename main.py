import os
import sqlite3
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import stripe

# --- Variabili d'ambiente ---
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
DATABASE_URL = os.environ.get("DATABASE_URL", "users.db")
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")

# --- Configurazioni Stripe ---
stripe.api_key = STRIPE_SECRET_KEY

# --- Flask app ---
flask_app = Flask(__name__)

# --- DB setup ---
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            vip INTEGER DEFAULT 0,
            matches_played INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()
    conn.close()
    await update.message.reply_text("Benvenuto! Puoi giocare fino a {} partite gratuite.".format(FREE_MAX_MATCHES))

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT vip, matches_played FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        vip, matches_played = row
        max_matches = VIP_MAX_MATCHES if vip else FREE_MAX_MATCHES
        if matches_played >= max_matches:
            await update.message.reply_text("Hai raggiunto il limite di partite!")
        else:
            matches_played += 1
            c.execute("UPDATE users SET matches_played = ? WHERE user_id = ?", (matches_played, user_id))
            conn.commit()
            await update.message.reply_text(f"Partita avviata! ({matches_played}/{max_matches})")
    conn.close()

# --- Telegram Bot setup ---
app_telegram = ApplicationBuilder().token(TG_BOT_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("play", play))

# --- Flask routes ---
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put_nowait(update)
    return "ok", 200

# Imposta webhook
async def set_webhook():
    await app_telegram.bot.set_webhook(WEBHOOK_URL + "/webhook")

# --- Avvio bot e Flask ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
