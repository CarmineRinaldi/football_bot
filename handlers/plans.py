from aiogram import types, Dispatcher
from .buttons import back_home
from utils.db import add_ticket, get_tickets
import os

FREE_MAX = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX = int(os.environ.get("VIP_MAX_MATCHES", 20))

async def plan_free(message: types.Message):
    await message.answer(f"🎉 Piano Free selezionato! Massimo {FREE_MAX} match al giorno.", reply_markup=back_home())
    # Qui inserire logica generazione schedine free
    add_ticket(message.from_user.id, "Schedina Free esempio ⚽")

async def plan_vip(message: types.Message):
    await message.answer(f"🏆 Piano VIP selezionato! Tutti i pronostici disponibili!", reply_markup=back_home())
    # Logica generazione schedine VIP
    add_ticket(message.from_user.id, "Schedina VIP esempio 🏆")

async def my_tickets(message: types.Message):
    tickets = get_tickets(message.from_user.id)
    if tickets:
        await message.answer("📋 Le tue schedine attuali:\n" + "\n".join(tickets), reply_markup=back_home())
    else:
        await message.answer("Non hai schedine attive 😢", reply_markup=back_home())

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(plan_free, lambda m: m.text and "Free" in m.text)
    dp.register_message_handler(plan_vip, lambda m: m.text and "VIP" in m.text)
    dp.register_message_handler(my_tickets, lambda m: m.text and "schedine" in m.text)
