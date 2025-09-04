from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import add_user, mark_started, has_started, add_pronostico, get_schedine, cleanup_schedine
import os
import asyncio

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

# Telegram bot setup
application = ApplicationBuilder().token(TOKEN).build()

# Comandi del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    if not has_started(user.id):
        mark_started(user.id)
    await update.message.reply_text("Benvenuto! Usa /schedina per inserire un pronostico e /le_mie_schedine per vedere le schedine degli ultimi 10 giorni.")

async def schedina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Devi scrivere un pronostico dopo il comando!")
        return
    add_pronostico(user.id, text)
    cleanup_schedine()
    await update.message.reply_text("Schedina salvata!")

async def le_mie_schedine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    schedine = get_schedine(user.id)
    if not schedine:
        await update.message.reply_text("Nessuna schedina trovata negli ultimi 10 giorni.")
        return
    msg = "Le tue schedine degli ultimi 10 giorni:\n"
    for s, date in schedine:
        msg += f"- {s} ({date})\n"
    await update.message.reply_text(msg)

# Aggiunta comandi
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("schedina", schedina))
application.add_handler(CommandHandler("le_mie_schedine", le_mie_schedine))

# Webhook Flask
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot attivo!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
