import os
import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import stripe

# -------------------------------
# Configurazioni e variabili
# -------------------------------
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile BOT_TOKEN!")
if not WEBHOOK_URL:
    raise ValueError("Devi impostare la variabile WEBHOOK_URL!")

# -------------------------------
# Inizializza bot e dispatcher
# -------------------------------
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# -------------------------------
# Configura Stripe
# -------------------------------
stripe.api_key = STRIPE_SECRET_KEY

# -------------------------------
# Funzioni helper
# -------------------------------
async def fetch_football_data(endpoint: str):
    """Richiesta dati API football"""
    url = f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}"
    headers = {"X-RapidAPI-Key": API_FOOTBALL_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

# -------------------------------
# Handlers
# -------------------------------
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Ciao <b>{message.from_user.full_name}</b>! ⚽\n"
        "Benvenuto nel bot di Football!\n"
        "Usa /matches per vedere le partite disponibili."
    )

@dp.message(Command(commands=["matches"]))
async def cmd_matches(message: types.Message):
    data = await fetch_football_data("fixtures?status=NS&league=39&season=2025")
    if "response" not in data or not data["response"]:
        await message.answer("Nessuna partita trovata al momento.")
        return

    text = "Ecco le prossime partite:\n\n"
    for match in data["response"][:FREE_MAX_MATCHES]:
        fixture = match["fixture"]
        teams = match["teams"]
        text += f"{teams['home']['name']} vs {teams['away']['name']} - {fixture['date'][:10]}\n"

    await message.answer(text)

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Hai scritto: {message.text}")

# -------------------------------
# Webhook setup
# -------------------------------
async def setup_webhook():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")

# -------------------------------
# Main
# -------------------------------
async def main():
    await setup_webhook()
    logging.info("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")

if __name__ == "__main__":
    asyncio.run(main())
