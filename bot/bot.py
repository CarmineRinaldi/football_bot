from aiogram import Bot, Dispatcher
import os

# Prende il token dal tuo environment su Render
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

# Crea l'oggetto Bot e Dispatcher
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)
