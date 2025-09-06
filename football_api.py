import os
import requests

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"X-Auth-Token": API_KEY}

# -----------------------------
# Recupera tutte le leghe di club
# -----------------------------
def get_leagues():
    res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS)
    data = res.json().get("response", [])
    # filtriamo solo leghe di club (tipo League)
    leagues = [l for l in data if l["league"]["type"] == "League"]
    return leagues

# -----------------------------
# Recupera solo competizioni nazionali
# -----------------------------
def get_national_teams():
    res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS)
    data = res.json().get("response", [])
    # filtriamo solo nazionali e coppe principali
    national_leagues = [l for l in data if l["league"]["type"] in ["National", "Cup"]]
    return national_leagues

# -----------------------------
# Recupera partite di una lega (club o nazionale)
# -----------------------------
def get_matches(league_id):
    res = requests.get(f"{BASE_URL}/fixtures?league={league_id}&season=2025", headers=HEADERS)
    return res.json().get("response", [])
