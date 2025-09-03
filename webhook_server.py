from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, decrement_pronostico
from football_api import get_pronostico
from payments import create_checkout_session
import logging
import asyncio

# -------------------------------
# Config logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Telegram Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    keyboard = [
        [InlineKeyboardButton("Pronostico Free", callback_data='free')],
        [InlineKeyboardButton("Compra 10 pronostici - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 10 al giorno", callback_data='vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'free':
        pronostico = get_pronostico()
        decrement_pronostico(user_id)
        await query.edit_message_text(pronostico)

    elif query.data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await query.edit_message_text(f"Acquista qui: {url}")

    elif query.data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await query.edit_message_text(f"Acquista VIP qui: {url}")

# -------------------------------
# Application Telegram
# -------------------------------
application = ApplicationBuilder().token(TG_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# 🔧 Inizializza bot (solo una volta)
asyncio.get_event_loop().run_until_complete(application.initialize())

# -------------------------------
# Webhook endpoint
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # Crea un loop temporaneo per processare l'update (compatibile Gunicorn)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(application.process_update(update))
    except Exception as e:
        logger.exception("Errore processando update:")
        return "error", 500
    finally:
        loop.close()

    return "ok"

# -------------------------------
# Endpoint per debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram attivo!"

# -------------------------------
# Endpoint per impostare webhook
# -------------------------------
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.bot.delete_webhook()
        return await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(setup_webhook())
    except Exception as e:
        logger.exception("Errore impostando il webhook")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        loop.close()

    if success:
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    else:
        return jsonify({"status": "error", "message": "Errore nell'impostazione del webhook"}), 500
