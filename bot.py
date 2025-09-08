import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BaseChat
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from handlers import start, plans, search

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ENV VARIABLES ---
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# --- BOT & DISPATCHER ---
bot = Bot(token=BOT_TOKEN, parse_mode=None)  # parse_mode non più supportato direttamente
dp = Dispatcher(storage=MemoryStorage())

# --- REGISTER HANDLERS ---
dp.include_router(start.router)
dp.include_router(plans.router)
dp.include_router(search.router)

# --- WEBHOOK SETUP ---
async def on_startup(app: web.Application):
    # Cancella eventuali webhook vecchi
    await bot.delete_webhook()
    # Imposta il nuovo webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Bot spento correttamente")

# --- AIOHTTP HANDLER ---
async def handle(request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(text="OK")  # Ignore non-json requests
    update = dp.bot.parse_update(data)
    await dp.process_update(update)
    return web.Response(text="OK")

# --- AIOHTTP APP ---
app = web.Application()
app.router.add_post("/", handle)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Avvio bot su porta {port}…")
    web.run_app(app, host="0.0.0.0", port=port)
