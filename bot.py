import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import (
    init_db, add_user, get_all_users, get_user, set_plan,
    set_user_categories, is_vip_user, get_user_tickets
)
from bot_logic import send_daily_to_user
from payments import handle_stripe_webhook

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Variabili d'ambiente ---
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Campionati disponibili
# =========================
LEAGUES = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]

# =========================
# Funzioni menu inline
# =========================
def main_menu_keyboard(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🏆 Scegli campionati", callback_data=f"menu_leagues:{user_id}"),
        InlineKeyboardButton("💎 Upgrade VIP", callback_data=f"upgrade_vip:{user_id}"),
        InlineKeyboardButton("💰 Acquista 10 schedine", callback_data=f"upgrade_pay:{user_id}"),
        InlineKeyboardButton("📄 I miei ticket", callback_data=f"my_tickets:{user_id}")
    )
    return markup

def leagues_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    for league in LEAGUES:
        markup.add(InlineKeyboardButton(league, callback_data=f"set_league:{user_id}:{league}"))
    markup.add(InlineKeyboardButton("🔙 Indietro", callback_data=f"back_menu:{user_id}"))
    return markup

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(
        user_id,
        "Benvenuto! Seleziona un'opzione dal menu:",
        reply_markup=main_menu_keyboard(user_id)
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    user_id = call.from_user.id

    # ---- Menu principale ----
    if data.startswith("menu_leagues"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Seleziona i campionati che ti interessano:",
            reply_markup=leagues_keyboard(user_id)
        )

    elif data.startswith("set_league"):
        _, uid, league = data.split(":", 2)
        uid = int(uid)
        user = get_user(uid)
        cats = user.get("categories", [])
        if league not in cats:
            cats.append(league)
            set_user_categories(uid, cats)
        bot.answer_callback_query(call.id, f"{league} aggiunto!")
    
    elif data.startswith("back_menu"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Menu principale:",
            reply_markup=main_menu_keyboard(user_id)
        )

    elif data.startswith("upgrade_vip"):
        if is_vip_user(user_id):
            bot.answer_callback_query(call.id, "Sei già VIP!")
        else:
            set_plan(user_id, "vip")
            bot.answer_callback_query(call.id, "🎉 Sei diventato VIP!")
            bot.send_message(user_id, "Ora riceverai pronostici premium!")

    elif data.startswith("upgrade_pay"):
        set_plan(user_id, "pay", quota=10)
        bot.answer_callback_query(call.id, "💰 Hai acquistato 10 schedine!")
        bot.send_message(user_id, "Puoi ora ricevere fino a 10 schedine speciali.")

    elif data.startswith("my_tickets"):
        tickets = get_user_tickets(user_id)
        if not tickets:
            bot.answer_callback_query(call.id, "Non hai ancora ticket.")
            return
        msg = "📄 I tuoi ticket:\n\n"
        for t in tickets[-5:]:
            preds = "\n".join(t['predictions'])
            created = t['created_at']
            msg += f"📅 {created} ({t.get('category','N/A')}):\n{preds}\n\n"
        bot.send_message(user_id, msg)

# =========================
# Webhook Telegram
# =========================
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        logger.info("📩 Update ricevuto da Telegram")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error("Errore webhook Telegram: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200

# =========================
# Admin endpoint
# =========================
@app.route("/admin/send_today", methods=["POST"])
def send_today():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return jsonify({"error": "Forbidden"}), 403
    try:
        for uid in get_all_users():
            send_daily_to_user(bot, uid)
    except Exception as e:
        logger.error("Errore invio pronostici: %s", e)
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "invio avviato"}), 200

# =========================
# Stripe webhook
# =========================
@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        success = handle_stripe_webhook(payload, sig_header)
    except Exception as e:
        logger.error("Errore webhook Stripe: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200 if success else 400

# =========================
# Health check
# =========================
@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200

# =========================
# Main
# =========================
if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")
    logger.info("Bot webhook impostato su %s/telegram", WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
