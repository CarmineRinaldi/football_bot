from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, decrement_pronostico, has_started, mark_started, get_schedine
from football_api import get_pronostico, get_campionati
from payments import create_checkout_session

import logging
import asyncio
import os

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Telegram Application
# -------------------------------
httpx_request = HTTPXRequest(connect_timeout=30, read_timeout=30, pool_timeout=60, connection_pool_size=50)
application = ApplicationBuilder().token(TG_BOT_TOKEN).request(httpx_request).build()

# -------------------------------
# Loop globale per creare task
# -------------------------------
loop = asyncio.get_event_loop()

# -------------------------------
# Inizializza l'application una volta sola
# -------------------------------
loop.run_until_complete(application.initialize())

# -------------------------------
# Funzioni utili
# -------------------------------
async def send_message(chat_id, user_id, text, reply_markup=None):
    msg = await application.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    application.bot_data[f"last_message_{user_id}"] = msg.message_id

async def delete_last_message(chat_id, user_id):
    last_msg_id = application.bot_data.get(f"last_message_{user_id}")
    if last_msg_id:
        try:
            await application.bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
        except Exception as e:
            logger.warning(f"Errore eliminando messaggio: {e}")

# -------------------------------
# Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not has_started(user_id):
        add_user(user_id)
        mark_started(user_id)

    keyboard = [
        [InlineKeyboardButton("🎁 Pronostico Free (5 schedine)", callback_data='free')],
        [InlineKeyboardButton("💰 Compra 10 schedine - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("⭐ VIP 4,99€ - Tutti i pronostici", callback_data='vip')],
        [InlineKeyboardButton("📋 Le mie schedine", callback_data='myschedine')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, user_id, '👋 Ciao amico del pallone! Benvenuto nel mondo delle schedine più pazze e allegre! 🎉', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Callback già risposto o fallito: {e}")

    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    await delete_last_message(chat_id, user_id)

    if data == 'free':
        decrement_pronostico(user_id)
        await show_campionati(chat_id, user_id)

    elif data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await send_message(chat_id, user_id, f"🛒 Ecco il link per le tue schedine: {url}")

    elif data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await send_message(chat_id, user_id, f"🌟 Benvenuto nel club VIP! Acquista qui: {url}")

    elif data == 'myschedine':
        schedine = get_schedine(user_id)
        if schedine:
            text = "📋 Ecco le tue schedine più fighe:\n" + "\n\n".join([f"{i+1}) {s[1]}" for i, s in enumerate(schedine)])
        else:
            text = "📋 Ops! Nessuna schedina ancora… ma non disperare, il divertimento arriva presto! 😎"
        await send_message(chat_id, user_id, text)

    elif data.startswith('camp_'):
        campionato = data.split('_', 1)[1]
        pronostico = get_pronostico(user_id, campionato)
        await send_message(chat_id, user_id, f"⚽ Ecco il pronostico per {campionato}:\n{pronostico}")

    elif data == 'back':
        await start(update, context)

async def show_campionati(chat_id, user_id):
    campionati = get_campionati()
    keyboard = [[InlineKeyboardButton(c, callback_data=f'camp_{c}')] for c in campionati]
    keyboard.append([InlineKeyboardButton("⬅️ Torna al menu principale", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, user_id, "⚽ Scegli il campionato che ti fa battere il cuore (o il portafoglio! 😉)", reply_markup=reply_markup)

# -------------------------------
# Registrazione Handlers
# -------------------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# -------------------------------
# Webhook
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Update ricevuto: {data}")

    update = Update.de_json(data, application.bot)
    # Crea task nel loop globale senza bloccare Flask
    asyncio.create_task(application.process_update(update))

    return "ok"

# -------------------------------
# Endpoint debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "✅ Bot Telegram attivo e pronto a divertirsi!"

# -------------------------------
# Impostazione webhook manuale
# -------------------------------
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.bot.delete_webhook()
        return await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    if loop.run_until_complete(setup_webhook()):
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    else:
        return jsonify({"status": "error", "message": "Errore impostando il webhook"}), 500

# -------------------------------
# Avvio Flask
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
