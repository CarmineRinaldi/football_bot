from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from buttons import main_menu

router = Router()

def register_handlers(dp):
    dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Benvenuto! Scegli un'opzione dal menu:", 
        reply_markup=main_menu
    )

@router.callback_query()
async def back_home(query: CallbackQuery):
    if query.data == "back_home":
        await query.message.edit_text(
            "Sei tornato al menu principale",
            reply_markup=main_menu
        )
