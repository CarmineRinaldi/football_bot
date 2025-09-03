from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from keyboards import start_keyboard
from utils import get_daily_tips, decrement_credits, load_tips, create_stripe_checkout, process_success
from database import update_user
from config import TOKEN

tips = load_tips()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/start success_"):
        data = update.message.text.split("_")
        user_id = int(data[1])
        plan = data[2]
        process_success(user_id, plan)
        await update.message.reply_text("✅ Pagamento ricevuto! Crediti aggiunti.")
    else:
        await update.message.reply_text(
            "Benvenuto! Scegli un'opzione:",
            reply_markup=start_keyboard()
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "get_tip":
        available = get_daily_tips(user_id)
        if available > 0:
            tip = tips.pop(0)
            decrement_credits(user_id)
            await query.message.reply_text(f"🎯 Ecco il tuo pronostico:\n{tip}")
        else:
            await query.message.reply_text("Non hai crediti disponibili, acquista un pacchetto o attiva VIP.")
    elif query.data == "buy_10":
        url = create_stripe_checkout(user_id, "10_credits")
        await query.message.reply_text(f"💳 Completa il pagamento qui: {url}")
    elif query.data == "vip":
        url = create_stripe_checkout(user_id, "vip")
        await query.message.reply_text(f"👑 Completa il pagamento VIP qui: {url}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot avviato...")
app.run_polling()
