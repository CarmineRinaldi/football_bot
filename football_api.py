import requests
from config import API_FOOTBALL_KEY

def get_pronostico():
    """
    Restituisce il prossimo pronostico della partita.
    """
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?next=1"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['response']:
            match = data['response'][0]['fixture']
            home = data['response'][0]['teams']['home']['name']
            away = data['response'][0]['teams']['away']['name']
            date = match['date']
            return f"Prossima partita: {home} vs {away} il {date}"
        else:
            return "Nessun pronostico disponibile al momento."
    
    except requests.RequestException as e:
        return f"Errore nel recupero del pronostico: {e}"


def get_campionati():
    """
    Restituisce la lista dei principali campionati di calcio.
    """
    return [
        "Serie A",
        "Serie B",
        "Premier League",
        "La Liga",
        "Bundesliga",
        "Ligue 1",
        "Champions League",
        "Europa League"
    ]
