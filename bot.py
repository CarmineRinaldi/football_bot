import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI DALL'ENVIRONMENT ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://tuo-bot.onrender.com/webhook
PORT = int(os.getenv("PORT", 8080))     # Render usa la variabile PORT

# --- CREA BOT E DISPATCHER ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- IMPORT HANDLER ---
from handlers import start, plans, search

# registra tutti gli handler
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

# --- HANDLER WEBHOOK ---
async def on_startup(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.session.close()
    logger.info("Bot chiuso correttamente.")

async def handle_webhook(request: web.Request):
    data = await request.json()
    update = dp.bot.update_factory(data)
    await dp.process_update(update)
    return web.Response(text="OK")

# --- APP AIOHTTP ---
app = web.Application()
app.router.add_post("/webhook", handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# --- RUN APP ---
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)
