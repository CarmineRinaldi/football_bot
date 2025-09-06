import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Prendi il token dalle environment variables
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Devi impostare BOT_TOKEN nelle environment variables!")

# Funzione comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Il bot è attivo.")

# Crea l'applicazione
application = Application.builder().token(TOKEN).build()

# Aggiungi handler
application.add_handler(CommandHandler("start", start))

# Se vuoi usare FastAPI/Starlette insieme, definisci un app ASGI
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Avvia il bot in background
    asyncio.create_task(application.run_polling())

@app.get("/")
async def root():
    return {"status": "Bot attivo!"}

# Avvio diretto (solo se eseguito localmente)
if __name__ == "__main__":
    application.run_polling()
