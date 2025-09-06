import os
import asyncio
import httpx
from fastapi import FastAPI, Request

# ======================================================
# Configurazioni
# ======================================================
BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

app = FastAPI()

# ======================================================
# Funzioni Helper
# ======================================================
async def send_message(chat_id, text, reply_markup=None):
    """Invio sicuro di messaggi Telegram con gestione errori."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
                "parse_mode": "Markdown"
            })
    except httpx.RequestError as e:
        print(f"Errore invio messaggio a Telegram: {e}")

def get_main_menu():
    """Menu principale con piani e schedine."""
    return {
        "text": "🎉 Benvenuto nel tuo bot calcistico super divertente! ⚽\nScegli un piano e iniziamo a creare le tue schedine!",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Free Plan 🆓", "callback_data": "plan_free"}],
                [{"text": "2€ Pack 💶", "callback_data": "plan_2eur"}],
                [{"text": "VIP Monthly 👑", "callback_data": "plan_vip"}],
                [{"text": "Le mie schedine 📋", "callback_data": "my_tickets"}]
            ]
        }
    }

def get_free_plan_menu():
    return {
        "text": "🆓 **Free Plan:** puoi creare fino a 5 partite per schedina. Scegli il tuo campionato preferito e divertiti!",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Scegli Campionato ⚽", "callback_data": "select_league_free"}],
                [{"text": "🔙 Indietro", "callback_data": "main_menu"}]
            ]
        }
    }

def get_select_league_menu():
    # Esempio di campionati disponibili
    leagues = ["Serie A 🇮🇹", "Premier League 🇬🇧", "La Liga 🇪🇸", "Bundesliga 🇩🇪"]
    keyboard = [[{"text": league, "callback_data": f"league_{league}"}] for league in leagues]
    keyboard.append([{"text": "🔙 Indietro", "callback_data": "plan_free"}])
    return {
        "text": "Seleziona il campionato che vuoi per la tua schedina:",
        "reply_markup": {"inline_keyboard": keyboard}
    }

# ======================================================
# Gestione Webhook
# ======================================================
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    try:
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if text == "/start":
                await send_message(chat_id, **get_main_menu())

        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_cb = callback["data"]

            # ==================================================
            # Gestione piani
            # ==================================================
            if data_cb == "main_menu":
                await send_message(chat_id, **get_main_menu())
            elif data_cb == "plan_free":
                await send_message(chat_id, **get_free_plan_menu())
            elif data_cb == "select_league_free":
                await send_message(chat_id, **get_select_league_menu())
            elif data_cb.startswith("league_"):
                league_name = data_cb.replace("league_", "")
                await send_message(chat_id, f"Hai scelto il campionato: {league_name}\nProssimo passo: scegli le partite!")
            elif data_cb == "plan_2eur":
                await send_message(chat_id, "💶 **2€ Pack:** Prossimamente qui potrai pagare tramite Stripe!")
            elif data_cb == "plan_vip":
                await send_message(chat_id, "👑 **VIP Monthly:** Prossimamente abbonamento mensile!")
            elif data_cb == "my_tickets":
                await send_message(chat_id, "📋 Ecco le tue schedine salvate (funzione in sviluppo).")

        return {"ok": True}
    except Exception as e:
        print(f"Errore nella gestione del webhook: {e}")
        return {"ok": False, "error": str(e)}
