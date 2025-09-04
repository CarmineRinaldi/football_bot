import os
import sqlite3
import threading
from flask import Flask, request, jsonify, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -------------------------------
# Config
# -------------------------------
DB_FILE = os.environ.get("DB_FILE", "users.db")
FREE_MAX_MATCHES = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.environ.get("VIP_MAX_MATCHES", 20))
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.environ.get("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.environ.get("STRIPE_PRICE_VIP")

import stripe
stripe.api_key = STRIPE_SECRET_KEY

# -------------------------------
# Flask App
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Database
# -------------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    match_data TEXT NOT NULL,
    is_vip INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# -------------------------------
# Telegram Bot
# -------------------------------
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Usa /nuova_schedina per creare una schedina e /paga_vip per diventare VIP!")

async def nuova_schedina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Controllo numero di schedine
    with db_lock:
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE user_id=? AND is_vip=0", (user_id,))
        count_free = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE user_id=? AND is_vip=1", (user_id,))
        count_vip = cursor.fetchone()[0]

    if count_free >= FREE_MAX_MATCHES:
        await update.message.reply_text(f"Hai raggiunto il limite FREE ({FREE_MAX_MATCHES}). Diventa VIP per {VIP_MAX_MATCHES} schedine!")
        return

    # Inserisci nuova schedina
    match_data = "esempio_match_data"  # Qui puoi prendere input reale dall'utente
    with db_lock:
        cursor.execute("INSERT INTO tickets (user_id, match_data) VALUES (?,?)", (user_id, match_data))
        conn.commit()

    await update.message.reply_text("Schedina creata con successo! ✅")

async def paga_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': STRIPE_PRICE_VIP,
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{WEBHOOK_URL}/pagamento_successo",
            cancel_url=f"{WEBHOOK_URL}/pagamento_errore",
            metadata={"user_id": str(user_id)}
        )
        await update.message.reply_text(f"Procedi al pagamento VIP: {checkout_session.url}")
    except Exception as e:
        await update.message.reply_text(f"Errore creazione pagamento: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("nuova_schedina", nuova_schedina))
application.add_handler(CommandHandler("paga_vip", paga_vip))

# -------------------------------
# Stripe Webhook
# -------------------------------
@app.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
    except Exception as e:
        print("Errore webhook:", e)
        return abort(400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['metadata']['user_id'])
        with db_lock:
            cursor.execute("UPDATE tickets SET is_vip=1 WHERE user_id=? AND is_vip=0", (user_id,))
            conn.commit()
        print(f"Utente {user_id} diventato VIP!")

    return jsonify({"status": "success"})

# -------------------------------
# Flask + Telegram
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot online 🚀"

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    from telegram.ext import CommandHandler
    import asyncio

    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
