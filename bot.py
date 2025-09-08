from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from config import TG_BOT_TOKEN, WEBHOOK_URL
from handlers import start, button
from database import init_db

app = Flask(__name__)
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot, None)

init_db()

dp.add_handler(CommandHandler('start', start))
dp.add_handler(CallbackQueryHandler(button))

@app.route('/', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return 'OK'

if __name__ == '__main__':
    bot.set_webhook(WEBHOOK_URL)
    app.run(host='0.0.0.0', port=5000)
