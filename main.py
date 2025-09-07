import os
import httpx
from fastapi import FastAPI, Request
from db import init_db, delete_old_tickets
from bot_logic import (
    start, show_main_menu, show_plan_info,
    show_alphabet_keyboard, show_filtered_options,
    show_matches, search_team_prompt, show_search_results
)
from stripe_webhook import handle_stripe_event

# --------------------------
# Setup
# --------------------------

init_db()
delete_old_tickets()

app = FastAPI()
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

# Stato utenti
user_search_mode = {}       # Modalità ricerca squadra
user_menu_stack = {}        # Stack menu per tasto indietro

# --------------------------
# Funzioni Telegram
# --------------------------

async def send_message(chat_id, text, reply_markup=None):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": "Markdown"
        })
        return res.json().get("result", {}).get("message_id")

async def delete_message(chat_id, message_id):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id": chat_id,
            "message_id": message_id
        })

async def send_waiting_message(chat_id):
    return await send_message(chat_id, "⏳ Attendere prego...")

# --------------------------
# Webhook
# --------------------------

@app.get("/")
async def root():
    return {"status": "Bot online!"}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("Webhook ricevuto:", data)

    chat_id = None
    plan = "free"

    # ---------- Messaggio normale ----------
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message_id = data["message"]["message_id"]
        text = data["message"].get("text")

        # Modalità ricerca squadra
        if user_search_mode.get(chat_id):
            query = text.strip()
            await delete_message(chat_id, message_id)
            type_ = user_search_mode[chat_id]["type"]
            plan = user_search_mode[chat_id]["plan"]
            response = show_search_results(query, plan, type_)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_search_mode.pop(chat_id)
            user_menu_stack.pop(chat_id, None)
            return {"status": 200}

        if text == "/start":
            await delete_message(chat_id, message_id)
            response = start(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id] = [("main_menu", None)]
            return {"status": 200}

    # ---------- Callback query ----------
    if "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]

        await delete_message(chat_id, message_id)
        waiting_msg_id = await send_waiting_message(chat_id)

        # ---------- Menu principale ----------
        if cb_data == "main_menu":
            response = show_main_menu(data, None)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id] = [("main_menu", None)]

        # ---------- Piani ----------
        elif cb_data.startswith("plan_"):
            plan = cb_data.split("_")[1]
            response = show_plan_info(data, None, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id] = [("plan_info", plan)]

        # ---------- Selezione Campionato/Nazionale ----------
        elif cb_data.startswith("select_type_"):
            parts = cb_data.split("_")
            type_ = parts[2]
            plan = parts[3]
            response = show_search_choice(type_, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id].append(("select_type", (type_, plan)))

        # ---------- Ricerca per lettera ----------
        elif cb_data.startswith("search_letter_"):
            parts = cb_data.split("_")
            type_ = parts[2]
            plan = parts[3]
            response = show_alphabet_keyboard(plan, type_)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id].append(("alphabet", (type_, plan)))

        # ---------- Ricerca per nome ----------
        elif cb_data.startswith("search_name_"):
            parts = cb_data.split("_")
            type_ = parts[2]
            plan = parts[3]
            user_search_mode[chat_id] = {"type": type_, "plan": plan}
            response = search_team_prompt(plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id].append(("search_team", plan))

        # ---------- Filtri per lettera ----------
        elif cb_data.startswith("filter_"):
            parts = cb_data.split("_")
            type_ = parts[1]
            letter = parts[2]
            plan = parts[3]
            response = show_filtered_options(type_, letter, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id].append(("filtered", (type_, letter, plan)))

        # ---------- Mostra partite ----------
        elif cb_data.startswith("league_") or cb_data.startswith("national_"):
            parts = cb_data.split("_")
            league_id = int(parts[1])
            plan = parts[2]
            response = show_matches(data, None, league_id, plan)
            await send_message(chat_id, response["text"], response.get("reply_markup"))
            user_menu_stack[chat_id].append(("matches", (league_id, plan)))

        # ---------- Indietro ----------
        elif cb_data == "back":
            if chat_id in user_menu_stack and len(user_menu_stack[chat_id]) > 1:
                user_menu_stack[chat_id].pop()
                last_menu = user_menu_stack[chat_id][-1]
                kind, param = last_menu

                if kind == "plan_info":
                    response = show_plan_info(data, None, param)
                elif kind == "select_type":
                    type_, plan = param
                    response = show_search_choice(type_, plan)
                elif kind == "alphabet":
                    type_, plan = param
                    response = show_alphabet_keyboard(plan, type_)
                elif kind == "filtered":
                    type_, letter, plan = param
                    response = show_filtered_options(type_, letter, plan)
                elif kind == "matches":
                    league_id, plan = param
                    response = show_matches(data, None, league_id, plan)
                elif kind == "search_team":
                    plan = param
                    response = search_team_prompt(plan)
                elif kind == "main_menu":
                    response = show_main_menu(data, None)

                await send_message(chat_id, response["text"], response.get("reply_markup"))

    return {"status": 200}

# --------------------------
# Stripe webhook
# --------------------------

@app.post("/stripe_webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    sig_header = req.headers.get("stripe-signature")
    return handle_stripe_event(payload, sig_header)
