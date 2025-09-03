# bot.py
import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import init_db, add_user, get_user, set_user_plan, get_all_users, get_user_tickets
from bot_logic import send_daily_to_user

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

# =========================
# Costanti categorie
# =========================
CATEGORIES = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]
PLANS = ["free", "vip", "pay"]

# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}") for cat in CATEGORIES]
    keyboard.add(*buttons)
    bot.send_message(user_id, "Benvenuto! Scegli il campionato di tuo interesse:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def select_category(call):
    user_id = call.from_user.id
    category = call.data.replace("cat_", "")
    user = get_user(user_id)
    user_categories = user.get("categories", [])
    if category not in user_categories:
        user_categories.append(category)
    set_user_plan(user_id, user.get("plan", "free"), categories=user_categories)
    bot.answer_callback_query(call.id, f"Categoria {category} selezionata!")
    bot.send_message(user_id, f"Hai scelto: {category}\nPuoi continuare a selezionare altre categorie.")

@bot.message_handler(commands=["plan"])
def show_plan(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    plan = user.get("plan", "free")
    categories = ", ".join(user.get("categories", []))
    bot.send_message(user_id, f"Piano attuale: {plan}\nCategorie selezionate: {categories}")

@bot.message_handler(commands=["upgrade"])
def upgrade(message):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="VIP Mensile", callback_data="plan_vip"),
        InlineKeyboardButton(text="Pay 10 schedine", callback_data="plan_pay")
    ]
    keyboard.add(*buttons)
    bot.send_message(user_id, "Scegli il piano a pagamento:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("plan_"))
def select_plan(call):
    user_id = call.from_user.id
    plan = call.data.replace("plan_", "")
    if plan not in PLANS:
        bot.answer_callback_query(call.id, "Piano non valido")
        return

    if plan == "vip":
        # Attivazione VIP diretta (per test, poi integra Stripe)
        set_user_plan(user_id, "vip")
        bot.answer_callback_query(call.id, "VIP attivato!")
        bot.send_message(user_id, "🎉 Sei diventato VIP! Ora riceverai pronostici premium.")
    elif plan == "pay":
        # Pay 10 schedine (qui dovrai integrare Stripe)
        set_user_plan(user_id, "pay", tickets_quota=10)
        bot.answer_callback_query(call.id, "Piano pay attivato!")
        bot.send_message(user_id, "🎉 Hai acquistato 10 schedine! Riceverai pronostici fino all’esaurimento.")

@bot.message_handler(commands=["mytickets"])
def mytickets(message):
    user_id = message.from_user.id
    tickets = get_user_tickets(user_id)
    if not tickets:
        bot.send_message(user_id, "Non hai ancora ticket disponibili.")
        return
    response = "📄 I tuoi ticket:\n\n"
    for t in tickets[-5:]:  # mostra gli ultimi 5
        preds = "\n".join(t["predictions"])
        response += f"📅 {t.get('category', 'N/A')}:\n{preds}\n\n"
    bot.send_message(user_id, response)

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
