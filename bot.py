import logging
import os
from aiogram import Bot, Dispatcher
from handlers import start, free, vip, search

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Registriamo i router
start.register_handlers(dp)
free.register_handlers(dp)
vip.register_handlers(dp)
search.register_handlers(dp)

if __name__ == "__main__":
    import asyncio
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/")
    logging.info("Bot avviato")
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
