import requests
import os
import random
import logging
import json
from datetime import date
from tickets import create_ticket, get_tickets  # nuovo modulo che gestisce schedine

logger = logging.getLogger(__name__)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

if not API_FOOTBALL_KEY:
    logger.error("Variabile API_FOOTBALL_KEY non trovata!")

# --- Recupero pronostici dal bookmaker ---
def get_daily_predictions(num_matches=5):
    """Recupera pronostici giornalieri da API-Football o genera casuali."""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&season=2025"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error("Errore API-Football: %s", e)
        data = {"response": []}

    predictions = []
    for match in data.get("response", [])[:num_matches]:
        home = match["fixture"]["homeTeam"]["name"]
        away = match["fixture"]["awayTeam"]["name"]
        outcome = random.choice(["1", "X", "2"])  # casuale per ora
        predictions.append(f"{home} vs {away} → {outcome}")

    # Se l'API non restituisce partite, genera dummy
    if not predictions:
        teams = ["Milan", "Inter", "Juventus", "Napoli", "Roma", "Lazio"]
        for _ in range(num_matches):
            home, away = random.sample(teams, 2)
            outcome = random.choice(["1", "X", "2"])
            predictions.append(f"{home} vs {away} → {outcome}")

    return predictions

# --- Genera e invia schedine al DB ---
def generate_daily_tickets(user_id, is_vip=0):
    """
    Crea le schedine giornaliere:
      - Free: 10 schedine max, 3 pronostici visibili
      - VIP: tutte le schedine con tutti i pronostici
    """
    all_predictions = get_daily_predictions(num_matches=6)  # 6 pronostici totali
    tickets_to_create = 10 if not is_vip else 10  # puoi aumentare per VIP
    for _ in range(tickets_to_create):
        # mescola pronostici per creare ticket casuali
        ticket_pronostici = random.sample(all_predictions, 3 if not is_vip else len(all_predictions))
        create_ticket(user_id, ticket_pronostici, vip_only=0 if not is_vip else 1)

# --- Invia schedine al bot ---
def send_daily_to_user(bot, user_id):
    from db import is_vip_user
    vip = is_vip_user(user_id)
    generate_daily_tickets(user_id, vip)
    tickets = get_tickets(user_id, vip)
    if not tickets:
        bot.send_message(user_id, "Non ci sono schedine disponibili oggi.")
        return

    for t in tickets:
        txt = f"📊 Schedina #{t['ticket_id']}:\n"
        for p in t['pronostici']:
            txt += f"- {p}\n"
        bot.send_message(user_id, txt)
