import requests
import os

API_KEY = os.getenv("API_FOOTBALL_KEY")

def get_leagues():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    res = requests.get(url, headers=headers).json()
    leagues = []
    for item in res.get("response", []):
        leagues.append({
            "name": item["league"]["name"],
            "id": item["league"]["id"]
        })
    return leagues

def get_matches(league_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?league={league_id}&next=5"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    res = requests.get(url, headers=headers).json()
    matches = []
    for f in res.get("response", []):
        fixture = f["fixture"]
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]
        matches.append(f"{home} vs {away} ({fixture['date'][:10]})")
    return matches
