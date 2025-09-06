from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Crea l'app FastAPI
app = FastAPI()

# Crea il bot Telegram
BOT_TOKEN = "YOUR_TOKEN_HERE"
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Funzione comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono attivo!")

bot_app.add_handler(CommandHandler("start", start))

# Endpoint webhook
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"ok": True}

# Imposta webhook all'avvio
@app.on_event("startup")
async def on_startup():
    webhook_url = "https://football-bot-ric2.onrender.com/webhook"
    await bot_app.bot.set_webhook(webhook_url)
    print(f"Webhook impostato su {webhook_url}")

# Opzionale: endpoint di test
@app.get("/")
def read_root():
    return {"status": "ok"}
