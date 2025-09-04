import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3/"

def get_leagues():
    """Restituisce la lista delle leghe"""
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(f"{BASE_URL}leagues", headers=headers)
    return response.json()

# Esempio: puoi aggiungere altre funzioni
def get_matches():
    """Restituisce le partite del giorno (modifica secondo le tue necessità)"""
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(f"{BASE_URL}fixtures?date=2025-09-04", headers=headers)
    return response.json()
