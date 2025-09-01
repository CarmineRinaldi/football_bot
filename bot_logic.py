# bot_logic.py
import requests
import os

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

def get_daily_predictions():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?league=39&season=2025"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    predictions = []
    for match in data.get("response", [])[:5]:
        home = match["fixture"]["homeTeam"]["name"]
        away = match["fixture"]["awayTeam"]["name"]
        predictions.append(f"{home} vs {away} → 1X2 casuale")
    return "\n".join(predictions)

def send_daily_to_user(bot, user_id):
    msg = get_daily_predictions()
    bot.send_message(user_id, f"📊 Pronostici del giorno:\n\n{msg}")
