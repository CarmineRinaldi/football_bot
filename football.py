import requests
from config import API_FOOTBALL_KEY

BASE_URL = "https://v3.football.api-sports.io/"

def get_matches(league_ids=None):
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    url = BASE_URL + "fixtures"
    params = {"league": ",".join(map(str, league_ids))} if league_ids else {}
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    # ritorna lista di partite con info base
    return [(m['fixture']['id'], m['teams']['home']['name'], m['teams']['away']['name']) for m in data.get('response', [])]

def get_prediction(fixture_id):
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    url = BASE_URL + f"predictions?fixture={fixture_id}"
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("response"):
        pred = data['response'][0]['predictions']['advice']
        return pred
    return "N/A"
