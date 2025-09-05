import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("TG_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def start_command(message: types.Message):
    await message.reply("Ciao! Sono il tuo bot di calcio!")

async def help_command(message: types.Message):
    await message.reply("Usa /start per iniziare!")

def start_bot():
    @dp.message_handler(commands=["start"])
    async def start(message: types.Message):
        await start_command(message)

    @dp.message_handler(commands=["help"])
    async def help_msg(message: types.Message):
        await help_command(message)

    executor.start_polling(dp, skip_updates=True)
