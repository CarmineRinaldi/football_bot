from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from football_api import get_leagues, get_matches
from db import add_user, get_user_tickets, add_ticket, can_create_prediction

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id)
    keyboard = [
        [InlineKeyboardButton("Scegli Campionato", callback_data="choose_league")],
        [InlineKeyboardButton("Nazionali", callback_data="choose_national")],
        [InlineKeyboardButton("Le mie schedine", callback_data="my_tickets")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Benvenuto! Scegli un'opzione:", reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == "choose_league":
        leagues = get_leagues()
        keyboard = [[InlineKeyboardButton(l['league']['name'], callback_data=f"league_{l['league']['id']}")] for l in leagues[:10]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Scegli un campionato:", reply_markup=reply_markup)

    elif query.data.startswith("league_"):
        league_id = int(query.data.split("_")[1])
        matches = get_matches(league_id)
        keyboard = []
        for m in matches[:10]:
            home = m['fixture']['home']['name']
            away = m['fixture']['away']['name']
            keyboard.append([InlineKeyboardButton(f"{home} vs {away}", callback_data=f"match_{m['fixture']['id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Scegli una partita:", reply_markup=reply_markup)

    elif query.data.startswith("match_"):
        match_id = int(query.data.split("_")[1])
        if can_create_prediction(user_id, max_per_day=5):
            add_ticket(user_id, match_id)
            query.edit_message_text("Pronostico registrato! Puoi farne massimo 5 al giorno.")
        else:
            query.edit_message_text("Hai già raggiunto il limite di 5 pronostici per oggi.")

    elif query.data == "choose_national":
        matches = get_matches(national=True)
        keyboard = []
        for m in matches[:10]:
            home = m['fixture']['home']['name']
            away = m['fixture']['away']['name']
            keyboard.append([InlineKeyboardButton(f"{home} vs {away}", callback_data=f"match_{m['fixture']['id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Scegli una nazionale:", reply_markup=reply_markup)

    elif query.data == "my_tickets":
        tickets = get_user_tickets(user_id)
        if tickets:
            text = "Le tue schedine:\n" + "\n".join([f"{t['match_id']}" for t in tickets])
        else:
            text = "Non hai ancora schedine."
        query.edit_message_text(text)
