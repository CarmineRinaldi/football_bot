from flask import Flask, request, jsonify
import os
import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db import init_db, add_user, get_all_users, get_user_tickets, get_user, set_plan, is_vip_user
from bot_logic import send_daily_to_user
from payments import create_vip_checkout_session, create_ticket_checkout_session, handle_stripe_webhook

# --- Config logging ---
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

# -------------------------------
# Costanti categorie
# -------------------------------
CATEGORIES = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]

# =========================
# Helpers menu
# =========================
def main_menu(user_id):
    user = get_user(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    markup.add(
        InlineKeyboardButton("📄 I miei ticket", callback_data="my_tickets"),
        InlineKeyboardButton("⚡ Aggiorna a VIP", callback_data="upgrade_vip"),
        InlineKeyboardButton("🎫 Acquista pacchetto ticket", callback_data="buy_ticket"),
        InlineKeyboardButton("🏟 Seleziona categorie", callback_data="select_categories")
    )
    return markup

def categories_menu(user_id):
    user = get_user(user_id)
    markup = InlineKeyboardMarkup()
    for cat in CATEGORIES:
        selected = "✅" if user and cat in user.get("categories", []) else ""
        markup.add(InlineKeyboardButton(f"{selected} {cat}", callback_data=f"cat_{cat}"))
    markup.add(InlineKeyboardButton("🔙 Indietro", callback_data="back_main"))
    return markup

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(user_id, "Benvenuto! Riceverai i pronostici ogni giorno!")
    bot.send_message(user_id, "Seleziona un'opzione dal menu:", reply_markup=main_menu(user_id))

@bot.callback_query_handler(func=lambda c: True)
def handle_callback(query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    if data == "my_tickets":
        tickets = get_user_tickets(user_id)
        if not tickets:
            bot.send_message(user_id, "Non hai ancora ticket registrati.")
        else:
            resp = ""
            for t in tickets[-5:]:
                preds = "\n".join(t["predictions"])
                resp += f"📅 {t['created_at']} [{t['category']}]\n{preds}\n\n"
            bot.send_message(user_id, resp)
        bot.send_message(user_id, "Menu principale:", reply_markup=main_menu(user_id))

    elif data == "upgrade_vip":
        if is_vip_user(user_id):
            bot.send_message(user_id, "Sei già VIP!")
        else:
            url = create_vip_checkout_session(user_id)
            if url:
                bot.send_message(user_id, f"Completa l'acquisto VIP qui: {url}")
            else:
                bot.send_message(user_id, "Errore nella creazione sessione VIP.")
        bot.send_message(user_id, "Menu principale:", reply_markup=main_menu(user_id))

    elif data == "buy_ticket":
        url = create_ticket_checkout_session(user_id, num_tickets=10)
        if url:
            bot.send_message(user_id, f"Acquista 10 ticket qui: {url}")
        else:
            bot.send_message(user_id, "Errore nella creazione sessione ticket.")
        bot.send_message(user_id, "Menu principale:", reply_markup=main_menu(user_id))

    elif data == "select_categories":
        bot.send_message(user_id, "Seleziona le categorie:", reply_markup=categories_menu(user_id))

    elif data.startswith("cat_"):
        cat = data.replace("cat_", "")
        user = get_user(user_id)
        current = user.get("categories", [])
        if cat in current:
            current.remove(cat)
        else:
            current.append(cat)
        set_plan(user_id, user.get("plan", "free"), categories=current)
        bot.send_message(user_id, "Categorie aggiornate!", reply_markup=categories_menu(user_id))

    elif data == "back_main":
        bot.send_message(user_id, "Menu principale:", reply_markup=main_menu(user_id))

# =========================
# Webhook Telegram
# =========================
@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    try:
        json_str = request.get_data(as_text=True)
        logger.info("📩 Update ricevuto da Telegram: %s", json_str)
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
