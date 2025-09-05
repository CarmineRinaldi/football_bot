import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# -------------------------------
# CONFIG
# -------------------------------
TOKEN = os.environ.get("TG_BOT_TOKEN")  # Inserisci il token come variabile d'ambiente
WEBHOOK_PATH = "/webhook"  # Endpoint webhook
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL completo del webhook su Render

# -------------------------------
# TELEGRAM HANDLERS
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Info", callback_data="info")],
        [InlineKeyboardButton("Aiuto", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ciao! Scegli un'opzione:", reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "info":
        await query.edit_message_text("Questo è un bot di esempio su Render.")
    elif query.data == "help":
        await query.edit_message_text("Usa /start per vedere il menu.")

# -------------------------------
# BUILD TELEGRAM APP
# -------------------------------
app_telegram = ApplicationBuilder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CallbackQueryHandler(callback_handler))

# Imposta webhook
async def setup_webhook():
    await app_telegram.bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_PATH}")

# -------------------------------
# FLASK APP
# -------------------------------
flask_app = Flask(__name__)

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    asyncio.run(app_telegram.update_queue.put(update))
    return "ok", 200

# -------------------------------
# AVVIO
# -------------------------------
if __name__ == "__main__":
    # Setup webhook async prima di avviare Gunicorn
    asyncio.run(setup_webhook())
    # Flask gestirà le richieste su Render
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
