from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.callback_query()
async def vip_menu(query: CallbackQuery):
    if query.data == "menu_vip":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Accedi a tutti i pronostici", callback_data="vip_all")
        )
        await query.message.edit_text("Sezione VIP:", reply_markup=markup)
