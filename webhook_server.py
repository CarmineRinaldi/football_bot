# =========================
# Handlers Telegram
# =========================
@bot.message_handler(commands=["list_users"])
def list_users_command(message):
    try:
        ids = get_all_users()
        txt = "Utenti registrati:\n" + ("\n".join(map(str, ids)) if ids else "Nessun utente.")
        bot.send_message(message.chat.id, txt)
        logger.info("Lista utenti inviata a %s", message.chat.id)
    except Exception as e:
        logger.exception("Errore handler /list_users: %s", e)
        bot.send_message(message.chat.id, "Si è verificato un errore nel recupero utenti.")

# Fallback: risponde a QUALSIASI messaggio (utile per test immediato)
@bot.message_handler(func=lambda m: True)
def echo(message):
    try:
        logger.info("Msg ricevuto da %s: %s", message.chat.id, message.text)
        bot.send_message(message.chat.id, f"Hai scritto: {message.text}")
    except Exception as e:
        logger.exception("Errore echo: %s", e)

# =========================
# Endpoint ADMIN
# =========================
def _is_admin(req) -> bool:
    token = req.args.get("token")
    if not token:
        logger.warning("Richiesta admin senza token")
        return False
    return token == ADMIN_TOKEN

@app.post("/admin/send_today")
def send_today():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        users = get_all_users()
        if not users:
            logger.info("Nessun utente a cui inviare pronostici")
            return jsonify({"status": "no_users"}), 200

        for uid in users:
            send_daily_to_user(bot, uid)
        logger.info("Pronostici inviati a %d utenti", len(users))
        return jsonify({"status": "invio avviato", "count": len(users)}), 200
    except Exception as e:
        logger.exception("Errore invio pronostici: %s", e)
        return jsonify({"error": "internal"}), 500

@app.post("/admin/set_webhook")
def admin_set_webhook():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        url = f"{WEBHOOK_URL.rstrip('/')}/telegram"
        bot.remove_webhook()
        bot.set_webhook(url=url, secret_token=TG_SECRET if TG_SECRET else None)
        info = bot.get_webhook_info()
        logger.info("Webhook impostato: %s", info.url)
        return jsonify({"status": "ok", "webhook": info.to_dict()}), 200
    except Exception as e:
        logger.exception("Errore set_webhook: %s", e)
        return jsonify({"error": "internal"}), 500

@app.post("/admin/delete_webhook")
def admin_delete_webhook():
    if not _is_admin(request):
        return jsonify({"error": "Forbidden"}), 403
    try:
        bot.delete_webhook(drop_pending_updates=False)
        info = bot.get_webhook_info()
        logger.info("Webhook eliminato: %s", info.url)
        return jsonify({"status": "ok", "webhook": info.to_dict()}), 200
    except Exception as e:
        logger.exception("Errore delete_webhook: %s", e)
        return jsonify({"error": "internal"}), 500

# =========================
# Webhook Stripe (lazy import)
# =========================
@app.post("/stripe/webhook")
def stripe_webhook():
    try:
        from payments import handle_stripe_webhook  # import "pigro"
    except Exception as e:
        logger.warning("Stripe non configurato o import fallito: %s", e)
        return jsonify({"error": "payments_not_configured"}), 501

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        ok = handle_stripe_webhook(payload, sig_header)
        if ok:
            logger.info("Webhook Stripe elaborato correttamente")
            return jsonify({"status": "ok"}), 200
        logger.warning("Webhook Stripe invalido")
        return jsonify({"error": "invalid"}), 400
    except Exception as e:
        logger.exception("Errore nel webhook Stripe: %s", e)
        return jsonify({"error": "internal"}), 500
