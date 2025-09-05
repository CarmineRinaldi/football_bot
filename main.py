import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from db import init_db, add_user, get_user, add_schedina, get_schedine, update_user_plan
from football_api import get_matches
from utils import format_schedina, make_inline_keyboard

init_db()
app = Flask(__name__)
bot = Bot(token=os.environ.get("TG_BOT_TOKEN"))
dispatcher = Dispatcher(bot, None, workers=0)

def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username)
    buttons = [("Free", "plan_free"), ("2€ - 10 schedine", "plan_2eur"), ("VIP 4,99€/mese", "plan_vip")]
    update.message.reply_text("Benvenuto! Scegli un piano:", reply_markup=make_inline_keyboard(buttons))

def callback(update, context):
    query = update.callback_query
    data = query.data
    user = get_user(query.from_user.id)
    query.answer()

    if data.startswith("plan_"):
        plan = data.split("_")[1]
        update_user_plan(user["id"], plan)
        buttons = [("Serie A","league_SA"),("Premier League","league_PL"),("Le mie schedine","my_schedules")]
        query.edit_message_text("Seleziona il campionato o le tue schedine:", reply_markup=make_inline_keyboard(buttons))

    elif data.startswith("league_"):
        league = data.split("_")[1]
        matches = get_matches(league)
        kb = [(f"{m['home']} vs {m['away']}", f"match_{m['id']}") for m in matches[:5]]
        query.edit_message_text("Scegli le partite da inserire nella schedina:", reply_markup=make_inline_keyboard(kb))

    elif data.startswith("match_"):
        match_id = int(data.split("_")[1])
        matches = get_matches(2025)
        match = next((m for m in matches if m["id"]==match_id), None)
        if match:
            add_schedina(user["id"], [match], [1.5])
            query.edit_message_text("Schedina aggiunta!")

    elif data == "my_schedules":
        schedine = get_schedine(user["id"])
        text = "\n\n".join([format_schedina(s["matches"], s["odds"]) for s in schedine])
        if not text: text = "Non hai schedine."
        query.edit_message_text(text)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(callback))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
