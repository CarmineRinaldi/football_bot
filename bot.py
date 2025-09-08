import os, logging, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from handlers import start, free, vip, search
from db import init_db

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Init DB
init_db()

# Registrazione handler
start.register_handlers(dp)
free.register_handlers(dp)
vip.register_handlers(dp)
search.register_handlers(dp)

# Webhook handler aiohttp
async def handle(request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        logging.exception(e)
        return web.Response(text="Error", status=500)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app):
    logging.info("🛑 Bot shutdown completato.")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=10000)
