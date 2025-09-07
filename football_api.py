import os
import requests
from datetime import datetime

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "X-Auth-Token": API_KEY}

# --------------------------
# Fetch leghe raw
# --------------------------
def _fetch_leagues_raw():
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("response", [])
    except Exception as e:
        print("Errore fetch leagues:", e)
        return []

# --------------------------
# Leghe e nazionali
# --------------------------
def get_leagues():
    data = _fetch_leagues_raw()
    seen_ids = set()
    seen_name_country = set()
    leagues = []

    for l in data:
        league = l.get("league", {})
        country = l.get("country", {})
        lid = league.get("id")
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""
        key_name_country = (name.strip().lower(), country_name.strip().lower())

        if lid in seen_ids or key_name_country in seen_name_country:
            continue

        seen_ids.add(lid)
        seen_name_country.add(key_name_country)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        leagues.append(l)

    leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return leagues

def get_national_teams():
    data = _fetch_leagues_raw()
    seen_ids = set()
    seen_name_country = set()
    national_leagues = []

    for l in data:
        league = l.get("league", {})
        country = l.get("country", {})
        lid = league.get("id")
        name = league.get("name", "")
        typ = (league.get("type") or "").lower()
        country_name = country.get("name") or country.get("code") or ""
        key_name_country = (name.strip().lower(), country_name.strip().lower())

        if lid in seen_ids or key_name_country in seen_name_country:
            continue

        seen_ids.add(lid)
        seen_name_country.add(key_name_country)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        national_leagues.append(l)

    national_leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return national_leagues

# --------------------------
# Partite
# --------------------------
def get_matches(league_id):
    try:
        url = f"{BASE_URL}/fixtures?league={league_id}"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json().get("response", [])
        if data:
            return data

        year = datetime.utcnow().year
        for s in (year, year-1, year+1):
            url_s = f"{BASE_URL}/fixtures?league={league_id}&season={s}"
            res = requests.get(url_s, headers=HEADERS, timeout=10)
            res.raise_for_status()
            data = res.json().get("response", [])
            if data:
                return data
        return []
    except Exception as e:
        print(f"Errore get_matches per lega {league_id}: {e}")
        return []

# --------------------------
# Ricerca squadra
# --------------------------
def search_teams(query):
    """
    Cerca squadre in tutte le leghe e nazionali che contengono la stringa 'query'.
    Ritorna lista di dict: {"team": <nome squadra>, "match_id": <id lega>}
    """
    query = query.lower()
    results = []

    for league in get_leagues() + get_national_teams():
        league_id = league["league"]["id"]
        matches = get_matches(league_id)
        for m in matches:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            fixture_id = m["fixture"]["id"]

            if query in home.lower():
                results.append({"team": home, "match_id": fixture_id})
            if query in away.lower():
                results.append({"team": away, "match_id": fixture_id})

    # Rimuove duplicati basati su team + match_id
    seen = set()
    unique_results = []
    for r in results:
        key = (r["team"], r["match_id"])
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results
