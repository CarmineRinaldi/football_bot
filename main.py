import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # es: https://tuoapp.onrender.com/webhook
PORT = int(os.environ.get("PORT", 8443))

flask_app = Flask(__name__)

# --- Handlers Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Info", callback_data="info")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Benvenuto! Scegli un'opzione:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "info":
        await query.edit_message_text(text="Queste sono le informazioni sul bot.")
    elif query.data == "help":
        await query.edit_message_text(text="Ecco come usare il bot...")

# --- Application Telegram ---
app_telegram = ApplicationBuilder().token(TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CallbackQueryHandler(button))

# --- Flask routes ---
@flask_app.route("/")
def index():
    return "Bot attivo!"

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "ok"

# --- Set Webhook quando il bot parte ---
async def setup_webhook():
    await app_telegram.bot.set_webhook(WEBHOOK_URL)

# --- Avvio bot asincrono ---
import asyncio
asyncio.get_event_loop().run_until_complete(setup_webhook())

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT)
