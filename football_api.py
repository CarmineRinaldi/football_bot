import os
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {"X-Auth-Token": API_KEY}

# Lista delle nazionali più comuni (puoi ampliare)
NATIONAL_TEAMS = [
    {"id": 1, "name": "Italy"},
    {"id": 2, "name": "Spain"},
    {"id": 3, "name": "France"},
    {"id": 4, "name": "Germany"},
    {"id": 5, "name": "England"},
]

def get_leagues():
    """
    Restituisce campionati nazionali principali e lega internazionali
    """
    res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS)
    leagues = res.json().get("response", [])
    
    # Filtra solo i campionati principali
    main_leagues = [l for l in leagues if l["league"]["type"] == "League"]
    
    return main_leagues

def get_matches(league_id=None, national=False):
    """
    Restituisce le partite della stagione 2025
    Se national=True restituisce le partite delle nazionali
    """
    if national:
        # Genera un esempio statico per nazionali, o puoi fare chiamate reali se esistono endpoint
        today = datetime.utcnow().strftime("%Y-%m-%d")
        matches = []
        for i, team in enumerate(NATIONAL_TEAMS):
            # dummy match con se stesso, puoi sostituire con API reali se disponibili
            matches.append({
                "fixture": {
                    "id": 1000 + i,
                    "home": {"name": team["name"]},
                    "away": {"name": team["name"]},  # placeholder, poi si sostituisce
                    "date": today
                }
            })
        return matches
    
    # Se league_id è fornito
    if league_id:
        res = requests.get(f"{BASE_URL}/fixtures?league={league_id}&season=2025", headers=HEADERS)
        return res.json().get("response", [])
    
    return []
