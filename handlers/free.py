from aiogram import Dispatcher, types
from buttons import back_button
from db import save_ticket

def register_handlers(dp: Dispatcher):
    @dp.callback_query(lambda c: c.data.startswith("menu_free"))
    async def free_menu(call: types.CallbackQuery):
        # Auto-elimina vecchio messaggio
        await call.message.delete()
        # Mostra scelta campionati/nazionali
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("Campionati", callback_data="free_leagues"),
            types.InlineKeyboardButton("Nazionali", callback_data="free_national")
        )
        keyboard.add(types.InlineKeyboardButton("🔙 Indietro", callback_data="back_home"))
        await call.message.answer("Seleziona una sezione:", reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data.startswith("free_leagues"))
    async def generate_ticket(call: types.CallbackQuery):
        await call.message.delete()
        ticket = "Schedina Free esempio: Roma vs Juventus 1X2"  # esempio
        save_ticket(call.from_user.id, ticket)
        await call.message.answer(f"🎫 La tua schedina:\n{ticket}", reply_markup=back_button)
