import os
import requests
from db import add_user, get_user_plan, add_ticket, get_user_tickets, delete_old_tickets
from football_api import get_leagues, get_matches, get_match_odds

FREE_MAX_MATCHES = int(os.getenv("FREE_MAX_MATCHES", 5))
VIP_MAX_MATCHES = int(os.getenv("VIP_MAX_MATCHES", 20))

delete_old_tickets()  # auto-pulizia schedine vecchie

def start(update, context):
    user_id = update['message']['from']['id']
    add_user(user_id)
    return show_main_menu(update, context)

def show_main_menu(update, context):
    # Mostra piani e opzioni
    return {"text": "Benvenuto! Scegli un piano o la tua schedina:", "keyboard": [["Free"], ["2€"], ["VIP"]]}

def show_leagues(update, context):
    leagues = get_leagues()
    keyboard = [[league["league"]["name"]] for league in leagues[:10]]
    keyboard.append(["Indietro"])
    return {"text": "Scegli un campionato:", "keyboard": keyboard}

def show_matches(update, context, league_name):
    leagues = get_leagues()
    league_id = next((l["league"]["id"] for l in leagues if l["league"]["name"] == league_name), None)
    if not league_id:
        return {"text": "Campionato non trovato.", "keyboard": [["Indietro"]]}
    matches = get_matches(league_id)
    keyboard = [[f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}"] for m in matches[:FREE_MAX_MATCHES]]
    keyboard.append(["Indietro"])
    return {"text": "Scegli le partite:", "keyboard": keyboard}

def create_ticket(update, context, selected_matches):
    user_id = update['message']['from']['id']
    add_ticket(user_id, selected_matches)
    return {"text": "Schedina salvata!", "keyboard": [["Menù principale"]]}
