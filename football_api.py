import os
import requests

API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

def get_leagues():
    url = f"{BASE_URL}/leagues"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["response"]
    return []

def get_matches(league_id):
    url = f"{BASE_URL}/fixtures?league={league_id}&season=2025"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["response"]
    return []

def get_match_odds(fixture_id):
    url = f"{BASE_URL}/odds?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["response"]
    return []
