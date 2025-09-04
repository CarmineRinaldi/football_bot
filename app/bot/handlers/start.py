from aiogram import Router, types
from aiogram.filters import CommandStart
from app.keyboards import main_menu
from app.db import crud
from app.db.base import SessionLocal
from app.utils.logger import logger


router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
# upsert user
db = SessionLocal()
try:
user = crud.upsert_user(db, message.from_user.id, message.from_user.username)
finally:
db.close()


text = (
"⚽ Benvenuto nel Club dei Pronostici! \n"
"Seleziona un'opzione e inizia a ricevere schedine generate come un vero esperto. 🏆\n\n"
"Scegli:"
)
await message.answer(text, reply_markup=main_menu())
