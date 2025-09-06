import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
from db import init_db, add_user, get_user, update_matches
from stripe_handler import handle_stripe_event
from football import get_leagues, get_matches

TOKEN = os.getenv("TG_BOT_TOKEN")
FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

# Inizializza DB
init_db()

# FastAPI per webhook Stripe
app = FastAPI()

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)

# Telegram bot
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("⚽ Campionati", callback_data="leagues")],
        [InlineKeyboardButton("💎 Diventa VIP", callback_data="vip")],
        [InlineKeyboardButton("ℹ️ Aiuto", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Ciao {update.effective_user.first_name}! 👋\n\n"
        "Benvenuto nel bot ⚽ *Football Matches*!\n\n"
        "👉 Con il piano gratuito puoi vedere fino a "
        f"{FREE_MAX_MATCHES} partite.\n"
        "👉 Con il piano VIP ottieni fino a "
        f"{VIP_MAX_MATCHES} partite + accesso prioritario!\n\n"
        "Scegli un'opzione dal menu qui sotto 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "ℹ️ *Come funziona il bot*\n\n"
        "• /start → Messaggio di benvenuto\n"
        "• /leagues → Mostra i campionati disponibili\n"
        "• /matches <league_id> → Mostra le prossime partite\n"
        "• /vip → Informazioni sull'abbonamento VIP\n"
        "• /tickets → Controlla quante partite hai usato\n",
        parse_mode="Markdown"
    )

async def vip_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "💎 *Diventa VIP!*\n\n"
        "Con l'abbonamento VIP ottieni:\n"
        f"✅ Fino a {VIP_MAX_MATCHES} partite\n"
        "✅ Accesso prioritario\n"
        "✅ Supporto dedicato\n\n"
        "👉 Per abbonarti vai su /start e clicca *Diventa VIP*!",
        parse_mode="Markdown"
    )

async def tickets_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = get_user(user_id)
    max_matches = VIP_MAX_MATCHES if user["plan"] == "vip" else FREE_MAX_MATCHES
    await update.message.reply_text(
        f"🎟️ Hai usato {user['matches_used']} partite su {max_matches} disponibili.\n"
        f"Il tuo piano attuale è: *{user['plan'].upper()}*",
        parse_mode="Markdown"
    )

# Aggiungi comandi
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("vip", vip_command))
application.add_handler(CommandHandler("tickets", tickets_command))

# Funzione per avviare bot e FastAPI insieme
def run():
    import uvicorn
    from threading import Thread
    Thread(target=lambda: application.run_polling()).start()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    run()
