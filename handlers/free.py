from aiogram import Dispatcher, types
from buttons import back_home
from db import save_ticket, get_free_count, increment_free
import os

FREE_MAX = int(os.getenv("FREE_MAX_MATCHES", 5))

async def free_section(message: types.Message):
    current = get_free_count(message.from_user.id)
    if current >= FREE_MAX:
        await message.answer("Hai raggiunto il limite giornaliero delle schedine free!", reply_markup=back_home)
        return

    increment_free(message.from_user.id)
    ticket = "Schedina Free: Juventus - Inter"  # placeholder
    save_ticket(message.from_user.id, ticket)
    await message.answer(f"Ecco la tua schedina free:\n{ticket}", reply_markup=back_home)

def register_handlers(dp: Dispatcher):
    dp.message.register(free_section, lambda m: m.text=="Free")
