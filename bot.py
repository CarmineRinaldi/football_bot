import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from handlers import start, plans, search

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# Registrazione handler
start.register_handlers(dp)
plans.register_handlers(dp)
search.register_handlers(dp)

async def on_startup(app):
    # 🔹 Rimuove eventuali webhook vecchi
    await bot.delete_webhook(drop_pending_updates=True)
    # 🔹 Imposta quello nuovo
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook impostato su {WEBHOOK_URL}")

async def handle(request):
    data = await request.json()
    update = dp.bot.update_class.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post("/webhook", handle)

app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
