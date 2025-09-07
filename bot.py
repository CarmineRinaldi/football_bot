import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
from aiohttp import web

# ----------------- LOGGING -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- ENVIRONMENT -----------------
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_HTTP_TOKEN = os.getenv("ADMIN_HTTP_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")

if not BOT_TOKEN:
    raise ValueError("Devi impostare la variabile TG_BOT_TOKEN!")

if not WEBHOOK_URL:
    raise ValueError("Devi impostare la variabile WEBHOOK_URL!")

# ----------------- BOT SETUP -----------------
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=types.ParseMode.HTML)
)
dp = Dispatcher()

# ----------------- COMMAND HANDLERS -----------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Ciao {message.from_user.full_name}! ⚽\n"
        "Sono il tuo FootballBot. Pronto a fare pronostici vincenti!"
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Lista comandi:\n"
        "/start - Avvia il bot\n"
        "/help - Mostra questo messaggio\n"
        "/matches - Visualizza i match disponibili"
    )

# Esempio di handler per match (puoi espandere con API football)
@dp.message(Command("matches"))
async def matches(message: Message):
    await message.answer(f"Mostro fino a {FREE_MAX_MATCHES} match gratuiti oggi!")

# ----------------- WEBHOOK SETUP -----------------
async def handle_webhook(request: web.Request):
    """Riceve richieste POST dal webhook di Telegram"""
    try:
        update = types.Update(**await request.json())
        await dp.feed_update(update)
    except Exception as e:
        logger.exception(e)
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    # Cancella eventuali webhook precedenti
    await bot.delete_webhook(drop_pending_updates=True)
    # Imposta il webhook
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.session.close()

# ----------------- RUN WEB SERVER -----------------
app = web.Application()
app.router.add_post(f"/{BOT_TOKEN}", handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    logger.info("⚽ FootballBot è online! Pronti a fare pronostici vincenti!")
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
