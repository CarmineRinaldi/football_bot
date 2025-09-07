import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, plans, search
from utils.db import init_db

# Inizializzazione database
init_db()

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN non impostato nelle variabili d'ambiente")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=types.ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Registrazione handlers
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

# Handler per callback dei pulsanti
from handlers.buttons import main_menu, back_home

async def handle_callback(query: types.CallbackQuery):
    data = query.data
    if data == "back":
        await query.message.edit_text("⬅️ Sei tornato indietro", reply_markup=back_home())
    elif data == "home":
        await query.message.edit_text("🏠 Torniamo alla Home", reply_markup=main_menu())
    elif data == "plan_free":
        from handlers.plans import plan_free
        await plan_free(query.message, bot)
    elif data == "plan_vip":
        from handlers.plans import plan_vip
        await plan_vip(query.message, bot)
    elif data == "my_tickets":
        from handlers.plans import my_tickets
        await my_tickets(query.message)
    else:
        await query.answer("Comando non riconosciuto")

dp.callback_query.register(handle_callback)

async def main():
    print("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
