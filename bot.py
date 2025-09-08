import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Importa gli handlers
from handlers import start, plans, search

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- VARIABILI AMBIENTE ---
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # già settata su Render
PORT = int(os.getenv("PORT", 8080))     # Render passa sempre PORT

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("TG_BOT_TOKEN e WEBHOOK_URL devono essere impostati!")

# --- CREA BOT E DISPATCHER ---
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# --- REGISTRA HANDLERS ---
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)


# --- CALLBACK STARTUP/SHUTDOWN ---
async def on_startup(app: web.Application):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.session.close()


# --- MAIN ---
def main():
    app = web.Application()

    # webhook path (Telegram manda gli update qui)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

    # collega dispatcher e bot all'app
    setup_application(app, dp, bot=bot)

    # startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # avvia server
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
