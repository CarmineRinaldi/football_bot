from aiogram import Dispatcher, types
from buttons import main_menu

def register_handlers(dp: Dispatcher):
    @dp.message(lambda message: message.text == "/start")
    async def start_cmd(message: types.Message):
        await message.answer("Benvenuto! Scegli un'opzione:", reply_markup=main_menu)
