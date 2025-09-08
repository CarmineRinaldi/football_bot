import os
import asyncio
import random
from aiogram import Router, types
from ..buttons import back_home
from utils.db import add_ticket, get_tickets

router = Router()

FREE_MAX = int(os.environ.get("FREE_MAX_MATCHES", 5))
VIP_MAX = int(os.environ.get("VIP_MAX_MATCHES", 20))

WAIT_MESSAGES = [
    "⚽ Sto dribblando tra i match per creare la tua schedina…",
    "🥅 Preparando i pronostici come Buffon para i rigori…",
    "🚀 Lanciando i tuoi match come Ronaldo al tiro da fuori area…",
    "🍿 Sta arrivando la tua schedina, non perdere il corner!",
    "🏃‍♂️ Corro tra i campi per selezionare le partite migliori!"
]

async def send_wait_message(chat_id, bot):
    msg = await bot.send_message(chat_id, random.choice(WAIT_MESSAGES))
    await asyncio.sleep(1.5)
    await msg.delete()

@router.message(lambda m: "Free" in m.text)
async def plan_free(message: types.Message):
    await send_wait_message(message.chat.id, message.bot)
    await message.answer(
        f"🎉 Piano Free selezionato! Massimo {FREE_MAX} match al giorno.",
        reply_markup=back_home()
    )
    add_ticket(message.from_user.id, "Schedina Free esempio ⚽")

@router.message(lambda m: "VIP" in m.text)
async def plan_vip(message: types.Message):
    await send_wait_message(message.chat.id, message.bot)
    await message.answer(
        "🏆 Piano VIP selezionato! Tutti i pronostici disponibili!",
        reply_markup=back_home()
    )
    add_ticket(message.from_user.id, "Schedina VIP esempio 🏆")

@router.message(lambda m: "schedine" in m.text.lower())
async def my_tickets(message: types.Message):
    tickets = get_tickets(message.from_user.id)
    if tickets:
        await message.answer(
            "📋 Le tue schedine attuali:\n" + "\n".join(tickets),
            reply_markup=back_home()
        )
    else:
        await message.answer("Non hai schedine attive 😢", reply_markup=back_home())
