import os
import asyncio
from fastapi import FastAPI
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Il tuo token già fornito
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "IL_TUO_TOKEN_QUI")

# Creazione dell'app Telegram
application = Application.builder().token(TOKEN).build()

# FastAPI app
app = FastAPI()

# --- Handlers Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Il bot è attivo ✅")

application.add_handler(CommandHandler("start", start))

# --- Startup di FastAPI ---
@app.on_event("startup")
async def startup_event():
    # Avvia il polling in background
    asyncio.create_task(application.run_polling())

# --- Root endpoint solo per verifica Render ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot in esecuzione!"}
