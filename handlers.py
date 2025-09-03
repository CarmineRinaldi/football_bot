from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import add_user, get_user, decrement_pronostico
from football_api import get_pronostico
from payments import create_checkout_session

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    add_user(user_id)
    keyboard = [
        [InlineKeyboardButton("Pronostico Free", callback_data='free')],
        [InlineKeyboardButton("Compra 10 pronostici - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 10 al giorno", callback_data='vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == 'free':
        pronostico = get_pronostico()
        decrement_pronostico(user_id)
        query.edit_message_text(pronostico)
    
    elif query.data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        query.edit_message_text(f"Acquista qui: {url}")
    
    elif query.data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        query.edit_message_text(f"Acquista VIP qui: {url}")
