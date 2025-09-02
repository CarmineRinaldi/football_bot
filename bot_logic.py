import requests
import os
import random
import logging

logger = logging.getLogger(__name__)
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

if not API_FOOTBALL_KEY:
    logger.error("Variabile API_FOOTBALL_KEY non trovata!")

def get_daily_predictions():
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
        return "Errore nel recupero dei pronostici."

    predictions = []
    for match in data.get("response", [])[:5]:
        home = match["fixture"]["homeTeam"]["name"]
        away = match["fixture"]["awayTeam"]["name"]
        outcome = random.choice(["1", "X", "2"])  # casuale
        predictions.append(f"{home} vs {away} → {outcome}")
    return "\n".join(predictions)

def send_daily_to_user(bot, user_id):
    msg = get_daily_predictions()
    try:
        bot.send_message(user_id, f"📊 Pronostici del giorno:\n\n{msg}")
    except Exception as e:
        logger.error("Errore invio pronostici a %s: %s", user_id, e)
