# bot.py
import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import init_db, add_user, get_user, set_vip, set_plan, decrement_ticket_quota, get_all_users
from bot_logic import generate_daily_tickets_for_user, send_daily_to_user

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Config environment
# =========================
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("TG_BOT_TOKEN o WEBHOOK_URL mancanti")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# =========================
# Categorie disponibili
# =========================
CATEGORIES = ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1"]

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(user_id, "Benvenuto! Scegli la tua categoria preferita per ricevere pronostici.")
    show_category_menu(user_id)

def show_category_menu(user_id):
    markup = InlineKeyboardMarkup()
    for cat in CATEGORIES:
        markup.add(InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    bot.send_message(user_id, "Seleziona la categoria:", reply_markup=markup)

def show_plan_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Free (3 pronostici giornalieri)", callback_data="plan_free"),
        InlineKeyboardButton("VIP (tutte le schedine giornaliere)", callback_data="plan_vip"),
        InlineKeyboardButton("Pay 2€ per 10 schedine", callback_data="plan_pay")
    )
    bot.send_message(user_id, "Scegli il tuo piano:", reply_markup=markup)

# =========================
# Callback query
# =========================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    data = call.data

    if data.startswith("cat_"):
        category = data.replace("cat_", "")
        user = get_user(user_id)
        set_plan(user_id, plan=user.get("plan", "free"), categories=[category])
        bot.send_message(user_id, f"Categoria impostata: {category}")
        show_plan_menu(user_id)
    elif data.startswith("plan_"):
        plan_choice = data.replace("plan_", "")
        if plan_choice == "free":
            set_plan(user_id, "free", ticket_quota=0)
            bot.send_message(user_id, "✅ Piano Free attivato. Riceverai 3 pronostici giornalieri.")
        elif plan_choice == "vip":
            set_vip(user_id, 1)
            bot.send_message(user_id, "🎉 Sei diventato VIP! Riceverai tutte le schedine giornaliere.")
        elif plan_choice == "pay":
            set_plan(user_id, "pay", ticket_quota=10)
            bot.send_message(user_id, "💶 Piano Pay attivato! Hai 10 schedine disponibili da consumare.")

# =========================
# Comandi utente
# =========================
@bot.message_handler(commands=["mytickets"])
def mytickets(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    tickets = generate_daily_tickets_for_user(user_id, vip=user.get("vip", False))
    if user.get("plan") == "pay" and user.get("ticket_quota", 0) > 0:
        decrement_ticket_quota(user_id, 1)
    if not tickets:
        bot.send_message(user_id, "Non ci sono schedine disponibili oggi.")
        return
    text = "📄 I tuoi ticket:\n\n"
    for idx, t in enumerate(tickets, 1):
        text += f"📅 Ticket {idx} ({t.get('category','N/A')}):\n"
        for i, p in enumerate(t["predictions"], 1):
            text += f"{i}. {p}\n"
        text += "\n"
    bot.send_message(user_id, text)

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
# Admin
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
