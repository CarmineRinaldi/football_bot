import os
import logging
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, add_user, get_user, set_user_plan, set_user_categories
from bot_logic import send_daily_to_user

# --- Config logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Variabili ambiente ---
TOKEN = os.environ.get("TG_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_TOKEN = os.environ.get("ADMIN_HTTP_TOKEN", "metti_un_token_lungo")

if not TOKEN or not WEBHOOK_URL:
    logger.error("TG_BOT_TOKEN o WEBHOOK_URL mancanti!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- MENU INLINE ---
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 Scegli Campionato", callback_data="choose_league"),
        InlineKeyboardButton("💎 Scegli Piano", callback_data="choose_plan")
    )
    keyboard.row(
        InlineKeyboardButton("📄 I miei ticket", callback_data="my_tickets")
    )
    return keyboard

def league_keyboard():
    keyboard = InlineKeyboardMarkup()
    leagues = ["Premier League", "Serie A", "LaLiga", "Bundesliga", "Ligue 1"]
    for league in leagues:
        keyboard.add(InlineKeyboardButton(league, callback_data=f"league_{league}"))
    return keyboard

def plan_keyboard():
    keyboard = InlineKeyboardMarkup()
    plans = ["free", "vip", "pay"]
    for plan in plans:
        keyboard.add(InlineKeyboardButton(plan.capitalize(), callback_data=f"plan_{plan}"))
    return keyboard

# --- HANDLERS ---
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    bot.send_message(user_id, "Benvenuto! Naviga il menu qui sotto 👇", reply_markup=main_menu_keyboard())

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id

    # --- Scegli campionato ---
    if call.data == "choose_league":
        bot.send_message(user_id, "Seleziona il tuo campionato preferito:", reply_markup=league_keyboard())
    elif call.data.startswith("league_"):
        league = call.data.replace("league_", "")
        set_user_categories(user_id, [league])
        bot.send_message(user_id, f"Campionato selezionato: {league}", reply_markup=main_menu_keyboard())

    # --- Scegli piano ---
    elif call.data == "choose_plan":
        bot.send_message(user_id, "Seleziona il piano:", reply_markup=plan_keyboard())
    elif call.data.startswith("plan_"):
        plan = call.data.replace("plan_", "")
        set_user_plan(user_id, plan)
        bot.send_message(user_id, f"Piano selezionato: {plan.capitalize()}", reply_markup=main_menu_keyboard())

    # --- Mostra ticket ---
    elif call.data == "my_tickets":
        send_daily_to_user(bot, user_id)

# --- WEBHOOK FLASK ---
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

@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    init_db()
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/telegram")
    logger.info("Bot webhook impostato su %s/telegram", WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
