from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_user, add_schedina, get_schedine
from utils import waiting_message

def start(update, context: CallbackContext):
    add_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("Free", callback_data='plan_free')],
        [InlineKeyboardButton("2€ pack", callback_data='plan_2eur')],
        [InlineKeyboardButton("VIP 4,99€/mese", callback_data='plan_vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Benvenuto! Scegli un piano:", reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(waiting_message())
    # qui vai a gestire logica di free, VIP ecc con bottoni successivi
