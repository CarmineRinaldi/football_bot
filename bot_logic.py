from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import add_user, get_user_plan, add_ticket, get_user_tickets
from football_api import get_leagues, get_matches
import os

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, "free")
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.delete()
    keyboard = [
        [InlineKeyboardButton("Leagues", callback_data="leagues")],
        [InlineKeyboardButton("My Tickets", callback_data="tickets")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message("Main Menu:", reply_markup=reply_markup)

async def show_leagues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.delete()
    leagues = get_leagues()
    keyboard = [[InlineKeyboardButton(l["name"], callback_data=f"league_{l['id']}")] for l in leagues]
    keyboard.append([InlineKeyboardButton("Back", callback_data="main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message("Select League:", reply_markup=reply_markup)

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.delete()
    league_id = int(update.callback_query.data.split("_")[1])
    matches = get_matches(league_id)
    keyboard = [[InlineKeyboardButton(m, callback_data=f"match_{m}")] for m in matches]
    keyboard.append([InlineKeyboardButton("Back", callback_data="leagues")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message("Select Match:", reply_markup=reply_markup)

async def create_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.delete()
    user_id = update.effective_user.id
    plan = get_user_plan(user_id)
    tickets = get_user_tickets(user_id)
    max_tickets = VIP_MAX_MATCHES if plan == "vip" else FREE_MAX_MATCHES
    match = update.callback_query.data.split("_", 1)[1]
    if len(tickets) >= max_tickets:
        await update.effective_chat.send_message(f"You reached max tickets ({max_tickets})")
        return
    add_ticket(user_id, match)
    await update.effective_chat.send_message(f"Ticket added: {match}")
