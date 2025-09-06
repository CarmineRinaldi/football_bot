import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot_logic import start, show_main_menu, show_leagues, select_league, select_match, finish_ticket, show_tickets
from stripe_webhook import handle_stripe_event
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")
app = FastAPI()

bot_app = ApplicationBuilder().token(TOKEN).build()

# Commandi
bot_app.add_handler(CommandHandler("start", start))

# CallbackQueryHandler
bot_app.add_handler(CallbackQueryHandler(show_main_menu, pattern="^main_menu$"))
bot_app.add_handler(CallbackQueryHandler(show_leagues, pattern="^show_leagues$"))
bot_app.add_handler(CallbackQueryHandler(select_league, pattern="^select_league_"))
bot_app.add_handler(CallbackQueryHandler(select_match, pattern="^select_match_"))
bot_app.add_handler(CallbackQueryHandler(finish_ticket, pattern="^finish_ticket$"))
bot_app.add_handler(CallbackQueryHandler(show_tickets, pattern="^show_tickets$"))

@app.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)

@app.post("/telegram_webhook")
async def telegram_webhook(update: dict):
    upd = Update.de_json(update, bot_app.bot)
    await bot_app.process_update(upd)
    return {"status": "ok"}
