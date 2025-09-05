# main.py
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os

# --- Configurazione ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Assicurati di aver impostato questa variabile in Render

# --- Flask app ---
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot Telegram attivo!"

# --- Telegram Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono il tuo bot Telegram.")

# Creazione applicazione Telegram
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Aggiungi i comandi
app_telegram.add_handler(CommandHandler("start", start))

# --- Webhook per Render ---
@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    # Esegui aggiornamenti
    app_telegram.update_queue.put_nowait(update)
    return "OK"

# --- Main ---
if __name__ == "__main__":
    # Se vuoi testare in locale
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
