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

# 🔧 Inizializza bot e loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(application.initialize())
application.loop = loop  # assegna il loop all'applicazione

# -------------------------------
# Webhook endpoint
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    """Riceve update da Telegram e li processa in modo thread-safe."""
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    try:
        future = asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
        future.result(timeout=10)  # aspetta massimo 10 secondi
        return "ok"
    except Exception as e:
        logger.exception("Errore processando update:")
        return "error", 500

# -------------------------------
# Endpoint per debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram attivo!"

# -------------------------------
# Endpoint per impostare webhook da remoto
# -------------------------------
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    async def setup_webhook():
        await application.bot.delete_webhook()
        return await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

    try:
        success = asyncio.run_coroutine_threadsafe(setup_webhook(), application.loop).result()
    except Exception as e:
        logger.exception("Errore impostando il webhook")
        return jsonify({"status": "error", "message": str(e)}), 500

    if success:
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    else:
        return jsonify({"status": "error", "message": "Errore nell'impostazione del webhook"}), 500

# -------------------------------
# Avvio locale (solo debug)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
