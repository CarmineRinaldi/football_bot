from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_matches

user_state = {}

def delete_previous_message(update: Update, context: CallbackContext):
    try:
        if update.callback_query:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=update.callback_query.message.message_id)
        else:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=update.effective_message.message_id)
    except:
        pass

def start(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    keyboard = [
        [InlineKeyboardButton("Leagues", callback_data="show_leagues")],
        [InlineKeyboardButton("My Tickets", callback_data="show_tickets")]
    ]
    update.message.reply_text("Welcome! Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

def show_main_menu(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    keyboard = [
        [InlineKeyboardButton("Leagues", callback_data="show_leagues")],
        [InlineKeyboardButton("My Tickets", callback_data="show_tickets")]
    ]
    update.callback_query.message.reply_text("Main menu:", reply_markup=InlineKeyboardMarkup(keyboard))

def show_leagues(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    keyboard = [[InlineKeyboardButton(league, callback_data=f"select_league_{league}")] for league in get_leagues()]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
    update.callback_query.message.reply_text("Select a league:", reply_markup=InlineKeyboardMarkup(keyboard))

def select_league(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    league = update.callback_query.data.split("_")[-1]
    user_id = update.effective_user.id
    user_state[user_id] = {"league": league, "matches": []}

    matches = get_matches(league)
    keyboard = [[InlineKeyboardButton(f"{m['home']} vs {m['away']}", callback_data=f"select_match_{m['id']}")] for m in matches]
    keyboard.append([InlineKeyboardButton("Finish", callback_data="finish_ticket")])
    keyboard.append([InlineKeyboardButton("Back", callback_data="show_leagues")])
    update.callback_query.message.reply_text(f"Select matches for {league}:", reply_markup=InlineKeyboardMarkup(keyboard))

def select_match(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    match_id = update.callback_query.data.split("_")[-1]
    user_state[user_id]["matches"].append(match_id)
    update.callback_query.answer("Match added!")

def finish_ticket(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    user_id = update.effective_user.id
    state = user_state.get(user_id)
    if state:
        add_ticket(user_id, state["league"], state["matches"])
        del user_state[user_id]
        update.callback_query.answer("Ticket created!")
    show_main_menu(update, context)

def show_tickets(update: Update, context: CallbackContext):
    delete_previous_message(update, context)
    user_id = update.effective_user.id
    tickets = get_user_tickets(user_id)
    if not tickets:
        text = "No tickets found."
    else:
        text = ""
        for t in tickets:
            text += f"Ticket {t['ticket_id']} - {t['league']}:\n" + "\n".join(t['matches']) + "\n\n"
    keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
    update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
