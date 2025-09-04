import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3/"

def get_leagues():
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(f"{BASE_URL}leagues", headers=headers)
    return response.json()
