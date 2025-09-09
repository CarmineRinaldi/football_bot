import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://v3.football.api-sports.io/"

def get_matches(league_ids=None):
    """
    Ritorna una lista di tuple (fixture_id, home_team, away_team) per le partite.
    Se league_ids è fornito, filtra per quei campionati.
    """
    if not API_FOOTBALL_KEY:
        raise ValueError("API_FOOTBALL_KEY non impostata!")
    
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    url = BASE_URL + "fixtures"
    params = {"league": ",".join(map(str, league_ids))} if league_ids else {}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [(m['fixture']['id'], m['teams']['home']['name'], m['teams']['away']['name'])
                for m in data.get('response', [])]
    except requests.exceptions.RequestException as e:
        print(f"Errore API Football get_matches: {e}")
        return []

def get_prediction(fixture_id):
    """
    Ritorna il consiglio di pronostico per una singola partita (fixture_id)
    """
    if not API_FOOTBALL_KEY:
        raise ValueError("API_FOOTBALL_KEY non impostata!")
    
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    url = BASE_URL + f"predictions?fixture={fixture_id}"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("response"):
            pred = data['response'][0]['predictions']['advice']
            return pred
    except requests.exceptions.RequestException as e:
        print(f"Errore API Football get_prediction: {e}")
    
    return "N/A"
