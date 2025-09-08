from aiogram import Dispatcher, types
from buttons import back_home
from db import save_ticket

async def vip_section(message: types.Message):
    ticket = "Schedina VIP: Milan - Napoli"  # placeholder
    save_ticket(message.from_user.id, ticket)
    await message.answer(f"Ecco la tua schedina VIP:\n{ticket}", reply_markup=back_home)

def register_handlers(dp: Dispatcher):
    dp.message.register(vip_section, lambda m: m.text in ["Pack 2€", "VIP"])
