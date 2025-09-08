from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.callback_query()
async def search_menu(query: CallbackQuery):
    if query.data == "search":
        markup = InlineKeyboardMarkup()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            markup.add(InlineKeyboardButton(letter, callback_data=f"search_{letter}"))
        await query.message.edit_text("Cerca per lettera:", reply_markup=markup)
