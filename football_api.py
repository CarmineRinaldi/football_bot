import os
import requests

API_FOOTBALL_KEY = os.environ["API_FOOTBALL_KEY"]

HEADERS = {
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

def get_matches(league_id=None):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"season": 2025}  # esempio
    if league_id:
        params["league"] = league_id
    r = requests.get(url, headers=HEADERS, params=params)
    data = r.json()
    return data.get("response", [])
