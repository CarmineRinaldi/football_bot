import requests
import os

API_KEY = os.environ.get("API_FOOTBALL_KEY")

def get_matches(league):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"league": league, "season": 2025}
    r = requests.get(url, headers=headers, params=params).json()
    matches = []
    for f in r.get("response", []):
        matches.append({
            "id": f["fixture"]["id"],
            "home": f["teams"]["home"]["name"],
            "away": f["teams"]["away"]["name"],
            "odds": f.get("goals", 1.5)
        })
    return matches
