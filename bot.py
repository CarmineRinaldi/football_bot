from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TG_BOT_TOKEN, WEBHOOK_URL
from handlers import start, button
from database import init_db
import asyncio

app = Flask(__name__)

# Inizializza DB
asyncio.run(init_db())

# Crea l’app Telegram
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.create_task(application.process_update(update))
    return "OK"

if __name__ == "__main__":
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    app.run(host="0.0.0.0", port=5000)
