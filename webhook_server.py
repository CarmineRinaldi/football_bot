from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, decrement_pronostico, has_started, mark_started
from football_api import get_pronostico, get_campionati
from payments import create_checkout_session
import logging
import asyncio
import os

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask
app = Flask(__name__)

# Telegram Application
httpx_request = HTTPXRequest(connect_timeout=30, read_timeout=30, pool_timeout=120, connection_pool_size=200)
application = ApplicationBuilder().token(TG_BOT_TOKEN).request(httpx_request).build()

# -------------------------------
# Handlers
# -------------------------------
async def send_message(chat_id, text, reply_markup=None):
    await application.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if has_started(user_id):
        return

    add_user(user_id)
    mark_started(user_id)

    keyboard = [
        [InlineKeyboardButton("Pronostico Free (1 su 3 schedine su 10)", callback_data='free')],
        [InlineKeyboardButton("Compra 10 schedine - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 4,99€ - Tutti i pronostici", callback_data='vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, 'Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    if data == 'free':
        decrement_pronostico(user_id)
        await show_campionati(chat_id, user_id)
    elif data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await send_message(chat_id, f"Acquista qui: {url}")
    elif data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await send_message(chat_id, f"Abbonamento VIP attivo! Acquista qui: {url}")
    elif data.startswith('camp_'):
        campionato = data.split('_', 1)[1]
        pronostico = get_pronostico(user_id, campionato)
        await send_message(chat_id, f"Pronostico per {campionato}:\n{pronostico}")

async def show_campionati(chat_id, user_id):
    campionati = get_campionati()
    keyboard = [[InlineKeyboardButton(c, callback_data=f'camp_{c}')] for c in campionati]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, "Scegli il campionato:", reply_markup=reply_markup)

# Aggiunta handler
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# -------------------------------
# Webhook
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Update ricevuto: {data}")

    async def process_update():
        update = Update.de_json(data, application.bot)
        await application.initialize()  # <--- inizializza prima di process_update
        await application.process_update(update)
        await application.shutdown()    # <--- chiude risorse subito dopo

    asyncio.run(process_update())
    return "ok"

# Endpoint debug
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram attivo!"

# Impostazione webhook
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.initialize()
        await application.bot.delete_webhook()
        success = await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
        await application.shutdown()
        return success

    if asyncio.run(setup_webhook()):
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    else:
        return jsonify({"status": "error", "message": "Errore impostando il webhook"}), 500

# Avvio Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
