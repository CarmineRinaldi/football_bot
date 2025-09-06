import os
import stripe
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from db import add_user, get_user

# === ENV ===
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_2EUR = os.getenv("STRIPE_PRICE_2EUR")
STRIPE_PRICE_VIP = os.getenv("STRIPE_PRICE_VIP")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Stripe setup
stripe.api_key = STRIPE_SECRET_KEY

# FastAPI
app = FastAPI()

# Telegram Bot
bot_app = Application.builder().token(TG_BOT_TOKEN).build()

# === Commands ===
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("📊 Leagues", callback_data="leagues")],
        [InlineKeyboardButton("🎮 Matches", callback_data="matches")],
        [InlineKeyboardButton("💎 Diventa VIP", callback_data="vip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ Benvenuto su *FootballX Bot*! 🔥\n\n"
        "👉 Qui puoi seguire partite e campionati in tempo reale.\n"
        "Vuoi iniziare subito?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_cmd(update: Update, context):
    await update.message.reply_text(
        "ℹ️ Ecco i comandi disponibili:\n\n"
        "/start - Menù principale\n"
        "/help - Mostra questo messaggio\n"
        "/leagues - Lista dei campionati\n"
        "/matches - Partite disponibili\n"
        "/vip - Scopri i vantaggi VIP\n"
        "/profile - Il tuo profilo"
    )

async def profile(update: Update, context):
    user = get_user(update.message.from_user.id)
    plan = user["plan"] if user else "free"
    await update.message.reply_text(
        f"👤 Profilo:\nID: {update.message.from_user.id}\n"
        f"Piano attuale: {plan.upper()}"
    )

# === Callbacks ===
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "leagues":
        await query.edit_message_text("📊 Lista campionati in arrivo...")
    elif query.data == "matches":
        await query.edit_message_text("🎮 Partite disponibili...")
    elif query.data == "vip":
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": STRIPE_PRICE_VIP, "quantity": 1}],
            mode="subscription",
            success_url=WEBHOOK_URL,
            cancel_url=WEBHOOK_URL,
            client_reference_id=str(query.from_user.id)
        )
        await query.edit_message_text(
            "💎 Diventa VIP per sbloccare tutte le funzionalità!\n"
            f"[👉 Abbonati qui]({session.url})",
            parse_mode="Markdown"
        )

# === Handlers ===
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_cmd))
bot_app.add_handler(CommandHandler("profile", profile))
bot_app.add_handler(CallbackQueryHandler(button_handler))

# === Webhook (FastAPI) ===
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    update = Update.de_json(payload, bot_app.bot)
    await bot_app.process_update(update)
    return JSONResponse(content={"status": "ok"})
