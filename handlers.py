from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import add_user, get_schedine, add_schedina
from utils import waiting_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("Free", callback_data='plan_free')],
        [InlineKeyboardButton("2€ pack", callback_data='plan_2eur')],
        [InlineKeyboardButton("VIP 4,99€/mese", callback_data='plan_vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Benvenuto! Scegli un piano:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(await waiting_message())
    # TODO: logica Free/VIP
