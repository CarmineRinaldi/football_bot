from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, button_handler
from config import TG_BOT_TOKEN, WEBHOOK_URL

app = ApplicationBuilder().token(TG_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# Webhook
import logging
logging.basicConfig(level=logging.INFO)

async def main():
    await app.bot.set_webhook(WEBHOOK_URL)
    print("Bot in esecuzione con webhook...")
    await app.start()
    await app.updater.start_polling()  # fallback se webhook non funziona

import asyncio
asyncio.run(main())
