import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

headers = {
    "X-RapidAPI-Key": API_FOOTBALL_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

def get_today_matches():
    params = {"date": "2025-09-03"}  # puoi cambiare con data dinamica
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["response"]
    return []
