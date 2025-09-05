import os
import requests

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

def get_leagues():
    headers = {"X-Auth-Token": API_KEY}
    res = requests.get(f"{BASE_URL}/leagues", headers=headers)
    return res.json().get("response", [])

def get_matches(league_id):
    headers = {"X-Auth-Token": API_KEY}
    res = requests.get(f"{BASE_URL}/fixtures?league={league_id}&season=2025", headers=headers)
    return res.json().get("response", [])
