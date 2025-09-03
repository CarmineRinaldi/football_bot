from flask import Flask, request, jsonify
import os
import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_all_users, get_user, set_vip, set_plan
from bot_logic import send_daily_to_user
from payments import handle_stripe_webhook

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Telegram / Webhook ---
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Menu inline
# =========================
def main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🏆 Campionati", callback_data="choose_league"),
        InlineKeyboardButton("⭐ Upgrade VIP/Pay", callback_data="upgrade_plan")
    )
    markup.row(
        InlineKeyboardButton("📄 I miei ticket", callback_data="my_tickets")
    )
    return markup

def league_menu():
    markup = InlineKeyboardMarkup()
    leagues = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]
    for l in leagues:
        markup.add(InlineKeyboardButton(l, callback_data=f"league_{l}"))
    return markup

def upgrade_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("VIP - pronostici illimitati", callback_data="plan_vip"),
        InlineKeyboardButton("PAY - 2€ 10 schedine", callback_data="plan_pay")
    )
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
        "Benvenuto! Scegli una delle opzioni:",
        reply_markup=main_menu(user_id)
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "choose_league":
        bot.send_message(user_id, "Seleziona un campionato:", reply_markup=league_menu())
    elif data.startswith("league_"):
        league = data.replace("league_", "")
        user = get_user(user_id)
        categories = user.get("categories", [])
        if league not in categories:
            categories.append(league)
            set_plan(user_id, plan=user.get("plan", "free"), categories=categories)
        bot.send_message(user_id, f"Hai selezionato: {league}")
    elif data == "upgrade_plan":
        bot.send_message(user_id, "Scegli il tuo piano:", reply_markup=upgrade_menu())
    elif data == "plan_vip":
        set_vip(user_id, 1)
        bot.send_message(user_id, "🎉 Sei diventato VIP! Ora riceverai pronostici premium.")
    elif data == "plan_pay":
        # Per ora finta: in futuro integrazione Stripe
        set_plan(user_id, plan="pay", ticket_quota=10)
        bot.send_message(user_id, "💰 Hai acquistato 10 schedine pay! Riceverai pronostici premium.")
    elif data == "my_tickets":
        tickets = send_daily_to_user(bot, user_id)
        if tickets == 0:
            bot.send_message(user_id, "⚠️ Nessuna schedina disponibile oggi.")
    else:
        bot.send_message(user_id, "Comando non riconosciuto.")

# =========================
# Webhook Telegram
# =========================
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        logger.error("Errore webhook Telegram: %s", e)
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "ok"}), 200

# =========================
# Webhook Stripe
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
# Endpoint admin
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
