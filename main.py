import os
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import sqlite3
import stripe

# ======================
# Variabili d'ambiente
# ======================
TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
FREE_MAX_MATCHES = int(os.environ.get('FREE_MAX_MATCHES', 5))
VIP_MAX_MATCHES = int(os.environ.get('VIP_MAX_MATCHES', 20))
DATABASE_URL = os.environ.get('DATABASE_URL', 'users.db')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PRICE_VIP = os.environ.get('STRIPE_PRICE_VIP')

# ======================
# Stripe
# ======================
stripe.api_key = STRIPE_SECRET_KEY

# ======================
# Flask app
# ======================
app = Flask(__name__)

# ======================
# Bot Telegram
# ======================
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

# ======================
# DB helper
# ======================
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            matches_used INTEGER DEFAULT 0,
            vip INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user(chat_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT matches_used, vip FROM users WHERE chat_id=?", (chat_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(chat_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()

def increment_matches(chat_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET matches_used = matches_used + 1 WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

# ======================
# Comandi Telegram
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    add_user(chat_id)
    await update.message.reply_text(
        "Benvenuto! Usa /matches per vedere quante partite puoi ancora giocare."
    )

async def matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = get_user(chat_id)
    if not user:
        add_user(chat_id)
        user = get_user(chat_id)
    matches_used, vip = user
    max_matches = VIP_MAX_MATCHES if vip else FREE_MAX_MATCHES
    remaining = max_matches - matches_used
    await update.message.reply_text(f"Hai {remaining} partite rimanenti.")

async def buy_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': STRIPE_PRICE_VIP,
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{WEBHOOK_URL}/success?chat_id={chat_id}",
        cancel_url=f"{WEBHOOK_URL}/cancel?chat_id={chat_id}",
    )
    await update.message.reply_text(f"Completa il pagamento qui: {session.url}")

# ======================
# Aggiungi handler
# ======================
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("matches", matches))
application.add_handler(CommandHandler("buy_vip", buy_vip))

# ======================
# Webhook per Telegram
# ======================
@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# ======================
# Pagine test / Stripe
# ======================
@app.route("/")
def index():
    return "Bot Telegram attivo!"

@app.route("/success")
def success():
    chat_id = request.args.get("chat_id")
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("UPDATE users SET vip = 1 WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()
    return "Pagamento completato! Sei diventato VIP."

@app.route("/cancel")
def cancel():
    return "Pagamento annullato."

# ======================
# Imposta webhook appena parte Flask
# ======================
@app.before_first_request
def set_webhook():
    bot = application.bot
    bot.delete_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}/{TG_BOT_TOKEN}")

# ======================
# Avvio Flask
# ======================
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
