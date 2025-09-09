import threading
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import init_db
from handlers import start, button

app = Flask(__name__)
bot = Bot(token=TG_BOT_TOKEN)
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

# --- TELEGRAM HANDLERS ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# --- FLASK WEBHOOK ---
@app.route(f"/{TG_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run_coroutine_threadsafe(application.update_queue.put(update), telegram_loop)
    return "OK", 200

def main():
    init_db()

    global telegram_loop
    telegram_loop = asyncio.new_event_loop()
    t = threading.Thread(target=lambda: telegram_loop.run_forever(), daemon=True)
    t.start()

    # Imposta webhook
    asyncio.run_coroutine_threadsafe(bot.delete_webhook(), telegram_loop).result()
    asyncio.run_coroutine_threadsafe(bot.set_webhook(url=f"{WEBHOOK_URL}/{TG_BOT_TOKEN}"), telegram_loop).result()

    # Avvia Flask
    PORT = int(__import__('os').environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
