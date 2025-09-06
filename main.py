import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, Dispatcher

# --- Config ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # metti il token nelle variabili d'ambiente di Render
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

app = FastAPI()

# Crea il bot
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()
dispatcher: Dispatcher = application.bot_data.setdefault("dispatcher", application.dispatcher)

# --- Handler esempio ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono online 🚀")

application.add_handler(CommandHandler("start", start))

# --- FastAPI webhook endpoint ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await dispatcher.process_update(update)
    return {"ok": True}

# --- Startup & Shutdown ---
@app.on_event("startup")
async def startup_event():
    # Imposta il webhook su Telegram
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook impostato su {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    await bot.delete_webhook()
    print("Webhook eliminato al shutdown")
