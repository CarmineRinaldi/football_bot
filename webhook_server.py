from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, decrement_pronostico, has_started
from football_api import get_pronostico, get_campionati
from payments import create_checkout_session
import logging
import asyncio

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Application Telegram con pool e timeout
# -------------------------------
request_kwargs = {
    "connect_timeout": 30,
    "read_timeout": 30,
    "pool_timeout": 30,
    "connection_pool_size": 50,
}

application = ApplicationBuilder().token(TG_BOT_TOKEN).request_kwargs(request_kwargs).build()

# Inizializza bot
asyncio.get_event_loop().run_until_complete(application.initialize())

# -------------------------------
# Memorizzazione messaggi per auto-eliminazione
# -------------------------------
last_message = {}  # user_id -> message_id

async def send_with_delete_previous(user_id, chat_id, text, reply_markup=None):
    """Invia un messaggio eliminando il precedente dell'utente."""
    if user_id in last_message:
        try:
            await application.bot.delete_message(chat_id=chat_id, message_id=last_message[user_id])
        except:
            pass  # ignora errori se messaggio già cancellato

    msg = await application.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    last_message[user_id] = msg.message_id
    return msg

# -------------------------------
# Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if has_started(user_id):
        return  # se ha già cliccato start, non fa nulla

    add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("Pronostico Free (1 su 3 schedine su 10)", callback_data='free')],
        [InlineKeyboardButton("Compra 10 schedine - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 4,99€ - Tutti i pronostici", callback_data='vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_with_delete_previous(user_id, chat_id, 'Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    # --- Scelta del piano ---
    if data == 'free':
        decrement_pronostico(user_id)
        await show_campionati(user_id, chat_id)

    elif data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await send_with_delete_previous(user_id, chat_id, f"Acquista qui: {url}")

    elif data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await send_with_delete_previous(user_id, chat_id, f"Abbonamento VIP attivo! Acquista qui: {url}")

    # --- Scelta del campionato ---
    elif data.startswith('camp_'):
        campionato = data.split('_', 1)[1]
        pronostico = get_pronostico(user_id, campionato)
        await send_with_delete_previous(user_id, chat_id, f"Pronostico per {campionato}:\n{pronostico}")

# -------------------------------
# Funzioni helper
# -------------------------------
async def show_campionati(user_id, chat_id):
    campionati = get_campionati()
    keyboard = [[InlineKeyboardButton(c, callback_data=f'camp_{c}')] for c in campionati]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_with_delete_previous(user_id, chat_id, "Scegli il campionato:", reply_markup=reply_markup)

# -------------------------------
# Aggiunta handlers all'applicazione
# -------------------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# -------------------------------
# Webhook endpoint
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    """Riceve update da Telegram e li processa nel loop corretto."""
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # invia il task al loop di telegram
    future = asyncio.run_coroutine_threadsafe(
        application.process_update(update), application.bot.loop
    )
    try:
        future.result(timeout=5)  # cattura subito eventuali errori
    except Exception as e:
        logger.exception("Errore processando update")
        return jsonify({"status": "error", "message": str(e)}), 500

    return "ok"

# -------------------------------
# Endpoint debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram attivo!"

# -------------------------------
# Endpoint impostazione webhook
# -------------------------------
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.bot.delete_webhook()
        return await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    try:
        success = asyncio.get_event_loop().run_until_complete(setup_webhook())
    except Exception as e:
        logger.exception("Errore impostando il webhook")
        return jsonify({"status": "error", "message": str(e)}), 500

    if success:
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    else:
        return jsonify({"status": "error", "message": "Errore nell'impostazione del webhook"}), 500

# -------------------------------
# Avvio Flask (solo debug locale)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
