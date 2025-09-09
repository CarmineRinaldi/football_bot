from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import add_user, get_schedine, add_schedina, get_user, update_last_free
from utils import waiting_message, can_use_free
from config import FREE_MAX_MATCHES, VIP_MAX_MATCHES

def start(update: Update, context: CallbackContext):
    add_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("Free", callback_data='plan_free')],
        [InlineKeyboardButton("2€ pack", callback_data='plan_2eur')],
        [InlineKeyboardButton("VIP 4,99€/mese", callback_data='plan_vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Benvenuto! Scegli un piano:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_user(query.from_user.id)
    
    if query.data == 'plan_free':
        if user and can_use_free(user[3]):
            update_last_free(user[0])
            query.edit_message_text("✅ Puoi usare il piano Free per oggi!")
        else:
            query.edit_message_text("❌ Hai già usato il Free oggi, attendi 24h.")
    
    elif query.data == 'plan_2eur':
        query.edit_message_text("💶 Piano 2€ selezionato. Pagamento da implementare.")
    
    elif query.data == 'plan_vip':
        query.edit_message_text("⭐ Piano VIP selezionato. Pagamento da implementare.")
