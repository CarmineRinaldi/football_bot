from fastapi import FastAPI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from stripe_webhook import router as stripe_router
from db import init_db

app = FastAPI()
app.include_router(stripe_router)

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
init_db()

application = ApplicationBuilder().token(TG_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^main$"))
application.add_handler(CallbackQueryHandler(show_leagues, pattern="^leagues$"))
application.add_handler(CallbackQueryHandler(show_matches, pattern="^league_"))
application.add_handler(CallbackQueryHandler(create_ticket, pattern="^match_"))

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(application.start_polling())

