import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import (
    init_db, add_user, get_all_users, get_user, set_vip, is_vip_user,
    set_plan, set_user_categories, decrement_ticket_quota
)
from bot_logic import send_daily_to_user, generate_daily_tickets_for_user
from payments import handle_stripe_webhook

# =========================
# Config logging
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Variabili ambiente
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
# Inline keyboards
# =========================
def main_menu_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📄 Le mie schedine", callback_data="menu_tickets"),
        InlineKeyboardButton("⚡ Ricevi oggi", callback_data="menu_send_today")
    )
    kb.add(InlineKeyboardButton("🏆 Scegli campionati", callback_data="menu_categories"))
    kb.add(InlineKeyboardButton("💎 Upgrade piano", callback_data="menu_upgrade"))
    return kb

def categories_keyboard(user_categories):
    kb = InlineKeyboardMarkup()
    leagues = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]
    for league in leagues:
        label = f"✅ {league}" if league in user_categories else league
        kb.add(InlineKeyboardButton(label, callback_data=f"cat_{league}"))
    kb.add(InlineKeyboardButton("🔙 Menu principale", callback_data="menu_main"))
    return kb

def upgrade_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("💎 VIP Gratis (test)", callback_data="plan_vip"),
        InlineKeyboardButton("💰 Pay 2€ → 10 schedine", callback_data="plan_pay")
    )
    kb.add(InlineKeyboardButton("🔙 Menu principale", callback_data="menu_main"))
    return kb

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
        "Benvenuto! Usa il menu per gestire le tue schedine e scegliere il tuo piano.",
        reply_markup=main_menu_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user:
        bot.send_message(user_id, "Errore: utente non trovato.")
        return

    # ------------------------
    # Menu principale
    # ------------------------
    if call.data == "menu_main":
        bot.edit_message_text(
            "Menu principale:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )

    elif call.data == "menu_tickets":
        tickets = get_user_tickets(user_id)
        if not tickets:
            text = "Non hai ancora schedine."
        else:
            text = "📄 Le tue ultime schedine:\n\n"
            for t in tickets[-5:]:
                lines = [f"📅 {t['created_at']} ({t.get('category', 'N/A')})"]
                lines += [f"{i+1}. {p}" for i, p in enumerate(t['predictions'])]
                text += "\n".join(lines) + "\n\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_keyboard())

    elif call.data == "menu_send_today":
        tickets = generate_daily_tickets_for_user(user_id)
        send_daily_to_user(bot, user_id)
        bot.answer_callback_query(call.id, "Schedine inviate!")
        bot.edit_message_text("Schedine inviate oggi!", call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_keyboard())

    elif call.data == "menu_categories":
        kb = categories_keyboard(user.get("categories", []))
        bot.edit_message_text("Seleziona i campionati preferiti:", call.message.chat.id,
                              call.message.message_id, reply_markup=kb)

    elif call.data.startswith("cat_"):
        league = call.data[4:]
        categories = user.get("categories", [])
        if league in categories:
            categories.remove(league)
        else:
            categories.append(league)
        set_user_categories(user_id, categories)
        kb = categories_keyboard(categories)
        bot.edit_message_text("Aggiornato! Seleziona i campionati preferiti:", call.message.chat.id,
                              call.message.message_id, reply_markup=kb)

    elif call.data == "menu_upgrade":
        kb = upgrade_keyboard()
        bot.edit_message_text("Scegli il piano:", call.message.chat.id, call.message.message_id,
                              reply_markup=kb)

    elif call.data == "plan_vip":
        if is_vip_user(user_id):
            bot.answer_callback_query(call.id, "Sei già VIP!")
            return
        set_vip(user_id, 1)
        bot.edit_message_text("🎉 Sei diventato VIP! Ora riceverai pronostici premium.",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_keyboard())

    elif call.data == "plan_pay":
        # Imposta quota Pay per 10 schedine
        set_plan(user_id, "pay", quota=10)
        bot.edit_message_text("💰 Piano Pay attivato! Hai 10 schedine disponibili.",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=main_menu_keyboard())

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
