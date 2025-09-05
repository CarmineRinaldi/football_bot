from aiogram import Dispatcher, types
from app.utils.keyboards import main_menu, back_keyboard
from app.telegram_messages import WELCOME_TEXT
from app.db.session import SessionLocal
from app.db.models import User, Credit, Schedina
from app.services.api_football import get_leagues, get_matches, generate_advanced_schedina
from app.config import FREE_MAX_MATCHES, VIP_MAX_MATCHES

async def start_handler(message: types.Message):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id==str(message.from_user.id)).first()
    if not user:
        user = User(telegram_id=str(message.from_user.id), username=message.from_user.username)
        db.add(user)
        db.commit()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())
    db.close()
