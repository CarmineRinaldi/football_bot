import asyncio
import logging
import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
from config import TG_BOT_TOKEN, WEBHOOK_URL
from database import add_user, decrement_pronostico, has_started, mark_started, get_schedine
from football_api import get_pronostico, get_campionati
from payments import create_checkout_session
import nest_asyncio

nest_asyncio.apply()  # risolve problemi di "no running event loop"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------- Telegram ----------------
httpx_request = HTTPXRequest(connect_timeout=30, read_timeout=30)
application = ApplicationBuilder().token(TG_BOT_TOKEN).request(httpx_request).build()

last_message = {}

async def send_with_delete_previous(user_id, chat_id, text, reply_markup=None):
    if user_id in last_message:
        try:
            await application.bot.delete_message(chat_id=chat_id, message_id=last_message[user_id])
        except:
            pass
    msg = await application.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    last_message[user_id] = msg.message_id
    return msg

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

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not await has_started(user_id):
        await add_user(user_id)
        await mark_started(user_id)

    options = [
        ("🎯 Pronostico Free (5 schedine)", 'free'),
        ("💸 Compra 10 schedine - 2€", 'buy_10'),
        ("🌟 VIP 4,99€ - Tutti i pronostici", 'vip'),
        ("📋 Le mie schedine", 'myschedine')
    ]
    reply_markup = make_keyboard(options, add_back=False)
    await send_with_delete_previous(user_id, chat_id, "👋 Benvenuto! Scegli il tuo piano:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    await send_with_delete_previous(user_id, chat_id, "⏳ Caricamento...", reply_markup=None)

    if data == 'free':
        await decrement_pronostico(user_id)
        await show_campionati(user_id, chat_id)
    elif data == 'buy_10':
        url = create_checkout_session(user_id, "2eur")
        await send_with_delete_previous(user_id, chat_id, f"🛒 Acquista qui: {url}")
    elif data == 'vip':
        url = create_checkout_session(user_id, "vip")
        await send_with_delete_previous(user_id, chat_id, f"🌟 VIP! Acquista qui: {url}")
    elif data == 'myschedine':
        schedine = await get_schedine(user_id)
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
        await start(update, context)

# ---------------- Register handlers ----------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# ---------------- Flask webhook ----------------
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "✅ Bot Telegram attivo!"

@app.route("/set_webhook", methods=["GET"])
async def set_webhook():
    await application.bot.delete_webhook()
    success = await application.bot.set_webhook(WEBHOOK_URL + "/webhook")
    if success:
        return jsonify({"status": "ok", "message": "Webhook impostato correttamente!"})
    return jsonify({"status": "error", "message": "Errore nell'impostazione del webhook"}), 500

# ---------------- Run Flask ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
