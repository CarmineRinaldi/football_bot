from aiogram import types
from aiogram.filters import Command

async def cmd_search(message: types.Message):
    await message.answer("Funzione ricerca non ancora implementata.")

def register_handlers(dp):
    dp.message.register(cmd_search, Command(commands=["search"]))
