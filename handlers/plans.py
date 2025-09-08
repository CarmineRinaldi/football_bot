from aiogram import types
from aiogram.filters import Text
from buttons import plans_keyboard  # esempio markup

async def plan_free(message: types.Message):
    await message.answer("Ecco il piano Free!", reply_markup=plans_keyboard)

def register_handlers(dp):
    dp.message.register(plan_free, Text(text="Free"))
