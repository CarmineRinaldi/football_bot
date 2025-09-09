import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configurazione
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es. https://football-bot-ric2.onrender.com/<TOKEN>

app = Flask(__name__)

# Crea l'app Telegram
application = ApplicationBuilder().token(TOKEN).build()

# Esempio di comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Il bot è attivo ⚽")

application.add_handler(CommandHandler("start", start))

# Endpoint Flask per webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.update_queue.put(update))
    return "ok"

# Funzione principale per settare webhook e avviare Flask
async def main():
    # Imposta webhook (corretto con await)
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook settato su: {WEBHOOK_URL}")

    # Flask rimane in ascolto
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Avvia tutto
if __name__ == "__main__":
    asyncio.run(main())
