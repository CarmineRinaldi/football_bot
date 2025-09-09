import os
import sqlite3
import threading
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

from config import TG_BOT_TOKEN, WEBHOOK_URL, DATABASE_URL
from handlers import start, button
from stripe_payments import create_checkout_session, verify_webhook

# --- FLASK APP ---
app = Flask(__name__)

# --- TELEGRAM BOT ---
bot = Bot(token=TG_BOT_TOKEN)
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            is_vip INTEGER DEFAULT 0,
            last_free TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedine (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            match TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# --- STRIPE WEBHOOK ---
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    event = verify_webhook(request)
    if not event:
        return "Invalid webhook", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["success_url"].split("/")[-1])
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute("UPDATE users SET is_vip=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    return "", 200

# --- TELEGRAM WEBHOOK ---
@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run_coroutine_threadsafe(application.update_queue.put(update), telegram_loop)
    return "OK", 200

# --- MAIN ---
def main():
    init_db()

    # aggiungi handler Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # crea loop globale per Telegram
    global telegram_loop
    telegram_loop = asyncio.new_event_loop()
    t = threading.Thread(target=lambda: telegram_loop.run_forever(), daemon=True)
    t.start()

    # imposta webhook
    asyncio.run_coroutine_threadsafe(bot.delete_webhook(), telegram_loop).result()
    asyncio.run_coroutine_threadsafe(bot.set_webhook(url=f"{WEBHOOK_URL}/{TG_BOT_TOKEN}"), telegram_loop).result()

    # avvia Flask
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
