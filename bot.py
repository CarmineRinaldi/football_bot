import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import (
    init_db, add_user, get_all_users, get_user, set_user_plan,
    set_user_categories, get_user_tickets, decrement_ticket_quota
)
from bot_logic import send_daily_to_user, generate_daily_tickets_for_user
from payments import handle_stripe_webhook  # già implementato per VIP/Pay

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Lettura variabili / secrets
# =========================
def read_secret_file(name: str):
    try:
        path = f"/run/secrets/{name}"
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
    except Exception as e:
        logger.warning("Errore lettura secret file %s: %s", name, e)
    return None

TOKEN = os.environ.get("TG_BOT_TOKEN") or read_secret_file("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or read_secret_file("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN") or "metti_un_token_lungo"
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY") or read_secret_file("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET") or read_secret_file("STRIPE_ENDPOINT_SECRET")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY") or read_secret_file("API_FOOTBALL_KEY")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Menu inline
# =========================
def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📊 Scegli campionato", callback_data="choose_league"),
        InlineKeyboardButton("📋 Le mie schedine", callback_data="my_tickets"),
        InlineKeyboardButton("💎 Diventa VIP", callback_data="upgrade_vip"),
        InlineKeyboardButton("💰 Acquista schedine", callback_data="buy_pay")
    )
    return markup

def leagues_menu():
    markup = InlineKeyboardMarkup()
    leagues = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]
    for l in leagues:
        markup.add(InlineKeyboardButton(l, callback_data=f"league_{l}"))
    return markup

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    logger.info("Ricevuto /start da %s (%s)", user_id, username)
    add_user(user_id, username)
    bot.send_message(
        user_id,
        "⚽ Benvenuto nel bot pronostici! Usa il menu qui sotto per gestire i tuoi campionati e le schedine.",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    bot.send_message(message.chat.id, "📩 Hai scritto: " + message.text)

@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "choose_league":
        bot.send_message(user_id, "📊 Scegli il tuo campionato preferito:", reply_markup=leagues_menu())
    elif data.startswith("league_"):
        league = data.split("_", 1)[1]
        user = get_user(user_id)
        categories = user.get("categories", [])
        if league not in categories:
            categories.append(league)
        set_user_categories(user_id, categories)
        bot.send_message(user_id, f"✅ Hai aggiunto {league} ai tuoi campionati preferiti.", reply_markup=main_menu())
    elif data == "my_tickets":
        tickets = get_user_tickets(user_id)
        if not tickets:
            tickets = generate_daily_tickets_for_user(user_id)
        if not tickets:
            bot.send_message(user_id, "⚠️ Nessuna schedina disponibile al momento.")
        else:
            for idx, t in enumerate(tickets[:5], 1):
                txt = f"📋 Schedina {idx} ({t.get('category','N/A')}):\n"
                txt += "\n".join([f"{i+1}. {p}" for i, p in enumerate(t.get('predictions', []))])
                bot.send_message(user_id, txt)
    elif data == "upgrade_vip":
        user = get_user(user_id)
        if user.get("plan") == "vip":
            bot.send_message(user_id, "💎 Sei già un utente VIP!", reply_markup=main_menu())
        else:
            set_user_plan(user_id, "vip")
            bot.send_message(user_id, "🎉 Complimenti! Sei diventato VIP e avrai accesso illimitato ai pronostici.", reply_markup=main_menu())
    elif data == "buy_pay":
        user = get_user(user_id)
        if user.get("plan") == "pay" and user.get("ticket_quota", 0) > 0:
            bot.send_message(user_id, f"📋 Hai ancora {user['ticket_quota']} schedine disponibili.", reply_markup=main_menu())
        else:
            bot.send_message(user_id, "💰 Acquista un pacchetto da 2€ per ricevere 10 schedine extra (Stripe da integrare).", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "⚠️ Comando non riconosciuto.", reply_markup=main_menu())

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
# Admin endpoint
# =========================
@app.route("/admin/send_today", methods=["POST"])
def send_today():
    token = request.args.get("token")
    if token != ADMIN_TOKEN:
        return jsonify({"error": "Forbidden"}), 403
    for uid in get_all_users():
        send_daily_to_user(bot, uid)
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
