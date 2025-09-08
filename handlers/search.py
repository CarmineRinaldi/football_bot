from aiogram import Dispatcher, types
from buttons import back_button

def register_handlers(dp: Dispatcher):
    @dp.callback_query(lambda c: c.data.startswith("search"))
    async def search_menu(call: types.CallbackQuery):
        await call.message.delete()
        await call.message.answer("Cerca squadra o campionato:", reply_markup=back_button)
