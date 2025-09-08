from aiogram import Dispatcher, types
from buttons import main_menu

async def cmd_start(message: types.Message):
    await message.answer("Benvenuto! Scegli un'opzione dal menu:", reply_markup=main_menu)

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, commands=["start"])
