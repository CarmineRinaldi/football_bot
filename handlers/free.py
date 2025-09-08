from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.callback_query()
async def free_menu(query: CallbackQuery):
    if query.data == "menu_free":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Campionati", callback_data="free_leagues"),
            InlineKeyboardButton("Nazionali", callback_data="free_national")
        )
        await query.message.edit_text("Seleziona la categoria:", reply_markup=markup)
