import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Carica token dal .env
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

# Flask app
app = Flask(__name__)

# Telegram bot
app_telegram = ApplicationBuilder().token(TG_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Bot attivo.")

# Aggiungi handler
app_telegram.add_handler(CommandHandler("start", start))

# Webhook endpoint per Render
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "ok", 200

# Avvio bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(app_telegram.start())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
