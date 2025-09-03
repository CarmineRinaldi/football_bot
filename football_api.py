import requests
from config import API_FOOTBALL_KEY

def get_pronostico():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?next=1"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['response']:
        match = data['response'][0]['fixture']
        home = data['response'][0]['teams']['home']['name']
        away = data['response'][0]['teams']['away']['name']
        return f"Prossima partita: {home} vs {away} il {match['date']}"
    return "Nessun pronostico disponibile al momento."
