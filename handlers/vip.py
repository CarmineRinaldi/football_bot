from aiogram import Dispatcher, types
from buttons import back_button

def register_handlers(dp: Dispatcher):
    @dp.callback_query(lambda c: c.data.startswith("menu_vip"))
    async def vip_menu(call: types.CallbackQuery):
        await call.message.delete()
        await call.message.answer("Accedi ai pronostici VIP.", reply_markup=back_button)
