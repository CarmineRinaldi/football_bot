from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Text

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.callback_query(F.data.startswith("search"))
async def search_menu(query: CallbackQuery):
    markup = InlineKeyboardMarkup()
    # Lettere A-Z
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        markup.add(InlineKeyboardButton(letter, callback_data=f"search_{letter}"))
    await query.message.edit_text("Cerca per lettera:", reply_markup=markup)
