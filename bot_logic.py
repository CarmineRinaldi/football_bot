import requests
import os
import random
import logging
import json
from datetime import date
from db import is_vip_user
from tickets import create_ticket, get_tickets, delete_old_tickets

logger = logging.getLogger(__name__)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")
if not API_FOOTBALL_KEY:
    logger.error("Variabile API_FOOTBALL_KEY non trovata!")

# ----------------------------------------
# Funzioni principali
# ----------------------------------------

def fetch_matches():
    """Recupera partite da API Football (limitate a Premier League 39 per esempio)."""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&season=2025"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        logger.error("Errore API-Football: %s", e)
        return []

def generate_ticket(vip_only=0, max_matches=5):
    """Crea una schedina casuale."""
    matches = fetch_matches()
    if not matches:
        return ["Errore nel recupero delle partite."]

    ticket = []
    for match in matches[:max_matches]:
        home = match["fixture"]["homeTeam"]["name"]
        away = match["fixture"]["awayTeam"]["name"]
        outcome = random.choice(["1", "X", "2"])
        ticket.append(f"{home} vs {away} → {outcome}")

    # Se è free, mostra solo 3 pronostici a schedina
    if not vip_only:
        ticket = ticket[:3]

    return ticket

def generate_daily_tickets_for_user(user_id, is_vip):
    """Crea schedine giornaliere per un utente e le salva nel DB."""
    delete_old_tickets()  # pulizia giornaliera
    tickets_count = 10 if not is_vip else 15  # Free 10 ticket, VIP 15
    for _ in range(tickets_count):
        ticket = generate_ticket(vip_only=int(is_vip))
        create_ticket(user_id, ticket, vip_only=int(is_vip))

def get_user_daily_tickets(user_id):
    """Recupera schedine da mostrare all’utente a seconda del piano."""
    vip = is_vip_user(user_id)
    tickets = get_tickets(user_id, is_vip=vip)
    return tickets

def send_daily_to_user(bot, user_id):
    """Invia tutte le schedine giornaliere all’utente via Telegram."""
    vip = is_vip_user(user_id)
    tickets = get_user_daily_tickets(user_id)

    if not tickets:
        # Se non ci sono schedine, le generiamo
        generate_daily_tickets_for_user(user_id, vip)
        tickets = get_user_daily_tickets(user_id)

    msg_lines = []
    for t in tickets:
        pronos = t["pronostici"]
        msg_lines.append(f"🎟️ Schedina #{t['ticket_id']}:\n" + "\n".join(pronos))

    final_msg = "\n\n".join(msg_lines)
    try:
        bot.send_message(user_id, f"📊 Pronostici del giorno:\n\n{final_msg}")
    except Exception as e:
        logger.error("Errore invio pronostici a %s: %s", user_id, e)
