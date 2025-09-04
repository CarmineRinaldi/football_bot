import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3/"

def get_leagues():
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(f"{BASE_URL}leagues", headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Puoi filtrare o formattare i dati se vuoi
        leagues = [league['league']['name'] for league in data.get('response', [])]
        return "\n".join(leagues)
    else:
        return f"Errore API: {response.status_code}"
