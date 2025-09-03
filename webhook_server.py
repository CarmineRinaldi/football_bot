from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, get_user, decrement_pronostico
from football_api import get_pronostico
from payments import create_checkout_session

# -------------------------------
# Flask app e bot
# -------------------------------
app = Flask(__name__)
bot = Bot(token=TG_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# -------------------------------
# Comandi e callback
# -------------------------------
def start(update, context):
    user_id = update.effective_user.id
    add_user(user_id)
    keyboard = [
        [InlineKeyboardButton("Pronostico Free", callback_data='free')],
        [InlineKeyboardButton("Compra 10 pronostici - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 10 al giorno", callback_data='vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == 'free':
        pronostico = get_pronostico()
        decrement_pronostico(user_id)
        query.edit_message_text(pronostico)

    elif query.data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        query.edit_message_text(f"Acquista qui: {url}")

    elif query.data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        query.edit_message_text(f"Acquista VIP qui: {url}")

# -------------------------------
# Registrazione handler
# -------------------------------
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# -------------------------------
# Webhook endpoint
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# -------------------------------
# Endpoint per verifica e debug
# -------------------------------
@app.route("/", methods=["GET"])
def index():
    return "Bot Telegram attivo!"

# -------------------------------
# Avvio server (solo locale)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
