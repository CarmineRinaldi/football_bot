@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    # Messaggi testuali
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        message_id = data["message"]["message_id"]
        text = data["message"]["text"]

        if text == "/start":
            await delete_message(chat_id, message_id)
            response = start(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

    # Callback query
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]

        await delete_message(chat_id, message_id)

        if cb_data == "main_menu":
            response = show_main_menu(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data in ["plan_free", "plan_2eur", "plan_vip"]:
            plan = cb_data.split("_")[1]
            response = show_plan_info(data, None, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("select_league_"):
            plan = cb_data.split("_")[-1]
            response = show_leagues(data, None, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("league_"):
            parts = cb_data.split("_")
            league_id = int(parts[1])
            plan = parts[2]
            response = show_matches(data, None, league_id, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("match_"):
            parts = cb_data.split("_")
            match_id = int(parts[1])
            plan = parts[2]
            response = show_match_options(data, None, match_id, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))

        elif cb_data.startswith("predict_"):
            parts = cb_data.split("_")
            match_id = int(parts[1])
            prediction = parts[2]
            plan = parts[3]
            user_id = cb["from"]["id"]
            response = save_prediction(user_id, match_id, prediction)
