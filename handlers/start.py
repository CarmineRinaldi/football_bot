from aiogram import types
from aiogram.filters import Command
from buttons import main_menu  # import assoluto
import logging

async def cmd_start(message: types.Message):
    await message.answer("Benvenuto al bot!", reply_markup=main_menu)

def register_handlers(dp):
    dp.message.register(cmd_start, Command(commands=["start"]))
