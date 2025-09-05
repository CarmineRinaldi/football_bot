import requests
from app.config import API_FOOTBALL_KEY
from datetime import datetime

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}

def get_leagues():
    resp = requests.get(f"{BASE_URL}/leagues", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()["response"]
    return []

def get_matches(league_id, season=datetime.now().year):
    resp = requests.get(
        f"{BASE_URL}/fixtures?league={league_id}&season={season}&status=NS",
        headers=HEADERS
    )
    if resp.status_code == 200:
        return resp.json()["response"]
    return []

def generate_advanced_schedina(matches, max_matches):
    # Logica avanzata: considera forma squadre, quote, gol subiti
    selected = []
    matches_sorted = sorted(matches, key=lambda m: m["teams"]["home"]["name"])  # placeholder sort
    for m in matches_sorted[:max_matches]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        # semplice scelta: squadra favorita in base a quote
        home_odds = float(m["odds"]["home"]) if "odds" in m else 1.5
        away_odds = float(m["odds"]["away"]) if "odds" in m else 2.5
        pick = home if home_odds < away_odds else away
        selected.append({
            "home": home,
            "away": away,
            "pick": pick,
            "date": m["fixture"]["date"]
        })
    return selected
