import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

# ==========================
# CONFIGURAZIONE
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # deve essere impostato su Render
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # es: "https://nome-app.onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile BOT_TOKEN!")

# ==========================
# BOT E DISPATCHER
# ==========================
bot = Bot(
    token=BOT_TOKEN,
    default=types.DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=AiohttpSession()
)
dp = Dispatcher()

# ==========================
# HANDLER
# ==========================
@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    await message.answer(f"Ciao {message.from_user.full_name}! Bot attivo con webhook ✅")

# ==========================
# FUNZIONI WEBHOOK
# ==========================
async def on_startup():
    # Rimuove vecchi webhook e imposta quello nuovo
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook impostato:", WEBHOOK_URL)

async def on_shutdown():
    # Pulizia
    await bot.delete_webhook()
    await bot.session.close()
    print("Bot spento e webhook rimosso")

# ==========================
# SERVER WEB
# ==========================
async def handle(request):
    # Riceve aggiornamenti da Telegram
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)

# ==========================
# AVVIO BOT
# ==========================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    port = int(os.getenv("PORT", 8000))
    print(f"Bot avviato su porta {port}")
    web.run_app(app, port=port)
