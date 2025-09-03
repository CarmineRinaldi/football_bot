from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from config import TG_BOT_TOKEN
from keyboards import main_keyboard
from payments import create_payment_link
from database import SessionLocal, init_db, User
from datetime import datetime, timedelta

init_db()
session = SessionLocal()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Benvenuto! Scegli il tuo piano:",
        reply_markup=main_keyboard()
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == "free":
        user = session.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            user = User(telegram_id=str(user_id), plan="free", pronostics_left=1)
            session.add(user)
            session.commit()
        query.edit_message_text(f"Hai 1 pronostico gratuito! Ne rimangono: {user.pronostics_left}")

    elif query.data == "buy_10":
        url = create_payment_link(2)
        query.edit_message_text(f"Clicca qui per pagare 2€ e ricevere 10 pronostici: {url}")

    elif query.data == "vip":
        url = create_payment_link(10)  # prezzo VIP, es: 10€
        query.edit_message_text(f"Clicca qui per abbonarti VIP: {url}")

def main():
    updater = Updater(TG_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
