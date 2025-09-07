import os
import requests

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}  # header corretto per API-FOOTBALL


# -----------------------------
# Recupera tutte le leghe di club attive
# -----------------------------
def get_leagues():
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        data = res.json().get("response", [])
    except Exception as e:
        print("Errore get_leagues:", e)
        return []

    # filtriamo leghe di club attive (type = League) con stagione corrente
    leagues = []
    for l in data:
        if l["league"]["type"] == "League":
            # controllo se ha almeno una stagione recente
            seasons = l.get("seasons", [])
            if any(s.get("current") for s in seasons):
                leagues.append(l)

    return leagues


# -----------------------------
# Recupera solo competizioni nazionali
# -----------------------------
def get_national_teams():
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        data = res.json().get("response", [])
    except Exception as e:
        print("Errore get_national_teams:", e)
        return []

    # prendiamo coppe e nazionali con stagione corrente
    national_leagues = []
    for l in data:
        if l["league"]["type"] in ["Cup", "National"]:
            seasons = l.get("seasons", [])
            if any(s.get("current") for s in seasons):
                national_leagues.append(l)

    return national_leagues


# -----------------------------
# Recupera partite di una lega (club o nazionale)
# -----------------------------
def get_matches(league_id, season=2025):
    try:
        url = f"{BASE_URL}/fixtures?league={league_id}&season={season}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json().get("response", [])
        return data
    except Exception as e:
        print(f"Errore get_matches per lega {league_id}:", e)
        return []
