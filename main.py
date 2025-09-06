from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from bot_logic import start, button
from db import init_db
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
init_db()

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
