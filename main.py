import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

app = FastAPI()
bot = Bot(token=TOKEN)
telegram_app = Application.builder().token(TOKEN).build()

# --- Handler di esempio ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono online 🚀")

telegram_app.add_handler(CommandHandler("start", start))

# --- Endpoint webhook FastAPI ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await telegram_app.update_queue.put(update)
    await telegram_app.process_updates()
    return {"ok": True}

# --- Startup webhook ---
@app.on_event("startup")
async def startup_event():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook impostato su {WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    await bot.delete_webhook()
    print("Webhook eliminato al shutdown")
