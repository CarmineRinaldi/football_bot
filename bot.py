import os
from flask import Flask, request
from telegram import Update, Bot
import asyncio
import threading

from handlers import application  # importa l'applicazione Telegram e gli handler già configurati
from stripe_payments import handle_stripe_webhook, create_checkout_session
from database import init_db  # inizializzazione database

# --- CONFIG ---
TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 5000))

# --- FLASK APP ---
app = Flask(__name__)

# --- TELEGRAM WEBHOOK ENDPOINT ---
bot = Bot(token=TOKEN)

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run_coroutine_threadsafe(application.update_queue.put(update), telegram_loop)
    return "OK", 200

# --- STRIPE ROUTES ---
@app.route("/create-checkout-session/<price_id>/<int:user_id>", methods=["POST"])
def stripe_checkout(price_id, user_id):
    return create_checkout_session(price_id, user_id)

@app.route("/webhook", methods=["POST"])
def stripe_webhook_endpoint():
    return handle_stripe_webhook()

# --- MAIN ---
def main():
    # inizializza il database
    init_db()

    # crea loop globale per Telegram
    global telegram_loop
    telegram_loop = asyncio.new_event_loop()
    t = threading.Thread(target=lambda: telegram_loop.run_forever(), daemon=True)
    t.start()

    # imposta webhook Telegram
    from handlers import bot as telegram_bot
    asyncio.run_coroutine_threadsafe(telegram_bot.delete_webhook(), telegram_loop).result()
    asyncio.run_coroutine_threadsafe(
        telegram_bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}"), telegram_loop
    ).result()

    # avvia Flask
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
