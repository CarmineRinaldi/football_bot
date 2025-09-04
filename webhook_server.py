from database import add_schedina, get_schedine  # importa funzioni DB

# -------------------------------
# Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if has_started(user_id):
        return

    add_user(user_id)
    mark_started(user_id)

    keyboard = [
        [InlineKeyboardButton("Pronostico Free (1 su 3 schedine su 10)", callback_data='free')],
        [InlineKeyboardButton("Compra 10 schedine - 2€", callback_data='buy_10')],
        [InlineKeyboardButton("VIP 4,99€ - Tutti i pronostici", callback_data='vip')],
        [InlineKeyboardButton("Le mie schedine 📋", callback_data='myschedine')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, user_id, 'Benvenuto! Scegli il tuo piano:', reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Callback già risposto o fallito: {e}")

    user_id = query.from_user.id
    chat_id = query.message.chat.id
    data = query.data

    # Elimina subito il messaggio precedente
    await delete_last_message(chat_id, user_id)

    if data == 'free':
        decrement_pronostico(user_id)
        await show_campionati(chat_id, user_id)

    elif data == 'buy_10':
        url = create_checkout_session(user_id, price_id="price_2euro_10pronostici")
        await send_message(chat_id, user_id, f"Acquista qui: {url}")

    elif data == 'vip':
        url = create_checkout_session(user_id, price_id="price_vip_10al_giorno")
        await send_message(chat_id, user_id, f"Abbonamento VIP attivo! Acquista qui: {url}")

    elif data == 'myschedine':
        schedine = get_schedine(user_id)
        if schedine:
            text = "📋 Le tue ultime schedine:\n\n"
            for campionato, pronostico, data_creazione in schedine:
                text += f"🏆 {campionato} ({data_creazione}):\n➡️ {pronostico}\n\n"
        else:
            text = "📋 Non hai ancora schedine salvate."
        await send_message(chat_id, user_id, text)

    elif data.startswith('camp_'):
        campionato = data.split('_', 1)[1]
        pronostico = get_pronostico(user_id, campionato)
        
        # Salva la schedina in DB
        add_schedina(user_id, campionato, pronostico)

        await send_message(chat_id, user_id, f"Pronostico per {campionato}:\n{pronostico}")

    elif data == 'back':
        # Torna al menu principale
        await start(update, context)


async def show_campionati(chat_id, user_id):
    campionati = get_campionati()
    keyboard = [[InlineKeyboardButton(c, callback_data=f'camp_{c}')] for c in campionati]
    # aggiungo pulsante "Indietro"
    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(chat_id, user_id, "Scegli il campionato:", reply_markup=reply_markup)
