import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_all_users, get_user_tickets, is_vip_user, set_user_plan, get_user
from bot_logic import send_daily_to_user
from payments import create_vip_checkout_session, create_pay_package_session, handle_stripe_webhook

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Configurazione Bot
# =========================
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("Variabili TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Menu categorie
# =========================
CATEGORIES = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]

def main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📄 I miei ticket", callback_data="myticket"),
        InlineKeyboardButton("⭐ Diventa VIP", callback_data="upgrade_vip"),
        InlineKeyboardButton("💰 Pacchetto 10 schedine (2€)", callback_data="buy_pay")
    )
    return markup

def categories_markup():
    markup = InlineKeyboardMarkup()
    for cat in CATEGORIES:
        markup.add(InlineKeyboardButton(cat, callback_data=f"category_{cat}"))
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
        "Benvenuto! Scegli un'opzione dal menu:",
        reply_markup=main_menu_markup()
    )

# =========================
# Callback query
# =========================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    if data == "myticket":
        tickets = get_user_tickets(user_id)
        if not tickets:
            bot.send_message(user_id, "Non hai ancora ticket.")
        else:
            for idx, t in enumerate(tickets[-5:], 1):
                preds = "\n".join(t["predictions"])
                bot.send_message(user_id, f"📋 Schedina {idx} ({t.get('category','N/A')}):\n{preds}")
    elif data == "upgrade_vip":
        if is_vip_user(user_id):
            bot.send_message(user_id, "Sei già VIP!")
        else:
            url = create_vip_checkout_session(
                user_id,
                success_url=os.environ.get("STRIPE_SUCCESS_URL", "https://example.com/success"),
                cancel_url=os.environ.get("STRIPE_CANCEL_URL", "https://example.com/cancel")
            )
            if url:
                bot.send_message(user_id, f"🔥 Diventa VIP cliccando qui: {url}")
            else:
                bot.send_message(user_id, "Errore generazione link VIP, riprova più tardi.")
    elif data == "buy_pay":
        url = create_pay_package_session(
            user_id,
            success_url=os.environ.get("STRIPE_SUCCESS_URL", "https://example.com/success"),
            cancel_url=os.environ.get("STRIPE_CANCEL_URL", "https://example.com/cancel")
        )
        if url:
            bot.send_message(user_id, f"💰 Acquista 10 schedine: {url}")
        else:
            bot.send_message(user_id, "Errore generazione link pagamento, riprova più tardi.")
    elif data.startswith("category_"):
        cat = data.replace("category_", "")
        bot.send_message(user_id, f"Hai selezionato la categoria: {cat}")
        # eventuale logica per salvare preferenza utente
    else:
        bot.send_message(user_id, "Opzione non riconosciuta.")

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
    success = handle_stripe_webhook(payload, sig_header)
    return jsonify({"status": "ok"}), 200 if success else 400

# =========================
# Admin send
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
