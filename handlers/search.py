from aiogram import Dispatcher, types

async def search_team(message: types.Message):
    await message.answer("Scrivi il nome della squadra da cercare:")

def register_handlers(dp: Dispatcher):
    dp.message.register(search_team, lambda m: m.text=="Cerca squadra")
