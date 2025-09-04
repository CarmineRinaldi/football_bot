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
from telegram.error import BadRequest

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Telegram Application con pool ottimizzato
# -------------------------------
httpx_request = HTTPXRequest(connect_timeout=30, read_timeout=30, pool_timeout=120, connection_pool_size=20)
application = ApplicationBuilder().token(TG_BOT_TOKEN).request(httpx_request).build()

# -------------------------------
# Memorizzazione messaggi per auto-eliminazione
# -------------------------------
last_message = {}  # user_id -> message_id

async def send_with_delete_previous(user_id, chat_id, text, reply_markup=None):
    """Invia un messaggio eliminando il precedente dell'utente."""
    if user_id in last_message:
        try:
            await application.bot.delete_message(chat_id=chat_id, message_id=last_message[user_id])
        except BadRequest as e:
            if "message to delete not found" not in str(e):
                logger.warning(f"Impossibile eliminare messaggio precedente: {e}")

    msg = await application.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    last_message[user_id] = msg.message_id
    return msg

# -------------------------------
# Helper tastiere
# -------------------------------
def make_keyboard(options, add_back=True):
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in options]
    if add_back:
        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

async def show_campionati(user_id, chat_id):
    campionati = get_campionati()
    options = [(c, f'camp_{c}') for c in campionati]
    reply_markup = make_keyboard(options)
    await send_with_delete_previous(user_id, chat_id, "⚽ Scegli il campionato (non sbagliare 😎):", reply_markup=reply_markup)

# -------------------------------
# Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler comando /start"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not has_started(user_id):
        add_user(user_id)
        mark_started(user_id)

    options = [
        ("🎯 Pronostico Free (5 schedine)", 'free'),
        ("💸 Compra 10 schedine - 2€", 'buy_10'),
        ("🌟 VIP 4,99€ - Tutti i pronostici", 'vip'),
        ("📋 Le mie schedine", 'myschedine')
    ]
    reply_markup = make_keyboard(options, add_back=False)
    await send_with_delete_previous(user_id, chat_id, "👋 Benvenuto campione! Scegli il tuo piano o esplora le tue schedine:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler per tutti i callback button"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Callback già risposto o fallito: {e}")

    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    await send_with_delete_previous(user_id, chat_id, "⏳ Caricamento...", reply_markup=None)

    if data == 'free':
        decrement_pronostico(user_id)
        await show_campionati(user_id, chat_id)

    elif data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await send_with_delete_previous(user_id, chat_id, f"🛒 Acquista qui: {url}")

    elif data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await send_with_delete_previous(user_id, chat_id, f"🌟 VIP! Acquista qui: {url}")

    elif data == 'myschedine':
        schedine = get_schedine(user_id)
        if schedine:
            text = "📋 Le tue schedine:\n" + "\n\n".join([f"{i+1}) {s[1]}" for i, s in enumerate(schedine)])
        else:
            text = "📋 Le tue schedine:\n- Nessuna schedina disponibile 🤷‍♂️"
        reply_markup = make_keyboard([("⬅️ Indietro", "back")], add_back=False)
        await send_with_delete_previous(user_id, chat_id, text, reply_markup=reply_markup)

    elif data.startswith('camp_'):
        campionato = data.split('_', 1)[1]
        pronostico = get_pronostico(user_id, campionato)
        reply_markup = make_keyboard([("⬅️ Indietro", "back")], add_back=False)
        await send_with_delete_previous(user_id, chat_id, f"📊 Pronostico per {campionato}:\n{pronostico}", reply_markup=reply_markup)

    elif data == 'back':
        # Creiamo un update fittizio per start
        fake_update = Update(update.update_id, message=query.message)
        await start(fake_update, context)

# -------------------------------
# Registrazione Handlers
# -------------------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# -------------------------------
# Webhook stabile per Render
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"Update ricevuto: {data}")

    try:
        update = Update.de_json(data, application.bot)
        asyncio.create_task(application.process_update(update))
    except Exception as e:
        logger.exception("Errore processando update")
        return jsonify({"status": "error", "message": str(e)}), 500

    return "ok"

# -------------------------------
# Endpoint debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "✅ Bot Telegram attivo!"

# -------------------------------
# Impostazione webhook manuale
# -------------------------------
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.bot.delete_webhook()
        return await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    asyncio.create_task(setup_webhook())
    return jsonify({"status": "ok", "message": "Webhook impostato correttamente! (task in esecuzione)"})

# -------------------------------
# Avvio Flask
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
