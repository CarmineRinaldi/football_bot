import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------------------
# VARIABILI D'AMBIENTE
# ------------------------------
TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("Errore: la variabile TG_BOT_TOKEN non è impostata!")

# ------------------------------
# APP FLASK
# ------------------------------
flask_app = Flask(__name__)

# ------------------------------
# HANDLER DEL BOT
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono il tuo Football Bot ⚽️")

# ------------------------------
# CREAZIONE DELL'APPLICATION
# ------------------------------
app_telegram = ApplicationBuilder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))

# ------------------------------
# ROUTE WEBHOOK
# ------------------------------
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Riceve aggiornamenti da Telegram via webhook."""
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "ok", 200

@flask_app.route("/", methods=["GET"])
def index():
    return "Football Bot attivo!", 200

# ------------------------------
# AVVIO WEBHOOK SU RENDER
# ------------------------------
async def set_webhook():
    await app_telegram.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
