import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TG_BOT_TOKEN, WEBHOOK_URL
from handlers import start, button
from database import init_db

# Inizializza il DB
init_db()

# Crea l'app Telegram asincrona
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

# Aggiungi i comandi e callback
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

async def main():
    # Imposta il webhook
    await application.bot.set_webhook(WEBHOOK_URL)

    # Avvia il bot in modalità webhook (ascolta sulla porta di Render)
    await application.run_webhook(
        listen="0.0.0.0",
        port=5000,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())

