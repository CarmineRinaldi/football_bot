import os
import sqlite3
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import stripe
import asyncio

# --- CONFIG ---
TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATABASE_URL = os.getenv("DATABASE_URL", "users.db")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

# --- FLASK APP ---
app = Flask(__name__)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            is_vip INTEGER DEFAULT 0,
            matches_used INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('SELECT user_id, is_vip, matches_used FROM users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_user(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users(user_id) VALUES(?)', (user_id,))
    conn.commit()
    conn.close()

def increment_matches(user_id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('UPDATE users SET matches_used = matches_used + 1 WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()

# --- TELEGRAM BOT ---
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    await update.message.reply_text("Benvenuto! Usa /matches per vedere i tuoi match disponibili.")

async def matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        add_user(user_id)
        user = get_user(user_id)
    is_vip = user[1]
    used = user[2]
    max_matches = VIP_MAX_MATCHES if is_vip else FREE_MAX_MATCHES
    remaining = max_matches - used
    await update.message.reply_text(f"Hai {remaining} match disponibili.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - avvia il bot\n/matches - mostra match disponibili\n/help - mostra questo messaggio")

# --- STRIPE PAYMENT HANDLERS ---
@app.route("/create-checkout-session/<price_id>/<int:user_id>", methods=["POST"])
def create_checkout(price_id, user_id):
    session = stripe.checkout.Session.create(
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url=f"{WEBHOOK_URL}/success/{user_id}",
        cancel_url=f"{WEBHOOK_URL}/cancel/{user_id}",
    )
    return {"url": session.url}

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_ENDPOINT_SECRET)
    except Exception as e:
        return str(e), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["success_url"].split("/")[-1])
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('UPDATE users SET is_vip=1 WHERE user_id=?', (user_id,))
        conn.commit()
        conn.close()

    return "", 200

# --- TELEGRAM WEBHOOK ENDPOINT ---
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    # Usa il loop corrente senza asyncio.run()
    loop = asyncio.get_event_loop()
    loop.create_task(application.update_queue.put(update))
    return "OK", 200

# --- MAIN ---
def main():
    init_db()

    # Aggiungi handler Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("matches", matches))
    application.add_handler(CommandHandler("help", help_command))

    # Imposta webhook senza chiudere loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.delete_webhook())
    loop.run_until_complete(bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}"))

    # Avvia Flask
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
