import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Variabili da Render Environment
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

if not TG_BOT_TOKEN:
    raise ValueError("❌ TG_BOT_TOKEN non trovato negli environment variables di Render!")

# Flask app
app = Flask(__name__)

# Telegram bot
app_telegram = ApplicationBuilder().token(TG_BOT_TOKEN).build()

# Comando base
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Ciao! Il bot è online su Render!")

# Aggiungi handler
app_telegram.add_handler(CommandHandler("start", start))

# Endpoint webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "ok", 200

# Endpoint root per test
@app.route("/", methods=["GET"])
def index():
    return "✅ Football Bot è attivo!", 200
