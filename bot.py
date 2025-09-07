import os
import logging
import asyncio
from aiogram import types
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import Dispatcher
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI AMBIENTE ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("Devi impostare TG_BOT_TOKEN e WEBHOOK_URL nell'environment!")

# --- BOT & DISPATCHER ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# --- HANDLER BASE ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("⚽ Benvenuto su FootballBot!\nPronti a fare pronostici vincenti?")

# --- WEBHOOK HANDLER ---
async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Errore nel gestire update: {e}")
    return web.Response()

# --- EVENTI APP ---
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logger.info("Webhook eliminato.")

# --- MAIN ---
def main():
    app = web.Application()
    app.router.add_post("/", handle_webhook)  # Telegram invierà qui gli update
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
