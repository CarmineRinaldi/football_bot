from fastapi import FastAPI, Request
import httpx
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # assicurati di settare BOT_TOKEN nelle variabili d'ambiente
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()
last_messages = {}  # per salvare l'ultimo messaggio inviato per ogni chat


async def send_message(chat_id: int, text: str, reply_markup=None):
    """
    Invia un messaggio al bot Telegram e cancella il precedente se esiste
    """
    # cancella messaggio precedente
    if chat_id in last_messages:
        try:
            await httpx.AsyncClient().post(
                f"{BASE_URL}/deleteMessage",
                json={"chat_id": chat_id, "message_id": last_messages[chat_id]},
                timeout=10.0
            )
        except Exception:
            pass  # se fallisce, ignoriamo

    # invia nuovo messaggio
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = reply_markup

    resp = await httpx.AsyncClient().post(f"{BASE_URL}/sendMessage", json=data, timeout=10.0)
    result = resp.json()
    if result.get("ok"):
        last_messages[chat_id] = result["result"]["message_id"]
    return result


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    print("Webhook ricevuto:", update)

    chat_id = None
    response = {"text": "Errore inatteso!", "reply_markup": None}

    # gestione messaggio testuale
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            response["text"] = "🎉 Benvenuto nel tuo bot calcistico super divertente! ⚽\nScegli un piano e iniziamo!"
            response["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
                    [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
                    [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
                    [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
                ]
            }

    # gestione callback inline
    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["from"]["id"]
        data = query["data"]

        if data == "plan_free":
            response["text"] = "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina. Scegli il tuo campionato preferito!"
            response["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "Scegli Campionato ⚽", "callback_data": "select_league_free"}],
                    [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
                ]
            }
        elif data == "main_menu":
            response["text"] = "🎯 Menu principale"
            response["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
                    [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
                    [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
                    [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
                ]
            }
        # aggiungi qui altri callback (schedine, piani VIP, campionati...)

    if chat_id:
        await send_message(chat_id, response["text"], response.get("reply_markup"))

    return {"ok": True}
