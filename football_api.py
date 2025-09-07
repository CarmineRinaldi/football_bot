import os
import requests
from datetime import datetime

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "X-Auth-Token": API_KEY}

# --------------------------
# Funzioni interne
# --------------------------

def _fetch_leagues_raw():
    """Recupera tutte le leghe dal servizio API Football."""
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
    """Restituisce solo leghe di club."""
    data = _fetch_leagues_raw()
    seen_ids = set()
    leagues = []

    for l in data:
        league = l.get("league", {})
        lid = league.get("id")
        typ = (league.get("type") or "").lower()
        if typ != "league":
            continue  # solo leghe di club
        country = l.get("country", {})
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""

        if lid in seen_ids:
            continue
        seen_ids.add(lid)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        leagues.append(l)

    leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return leagues

def get_national_teams():
    """Restituisce competizioni nazionali/cup."""
    data = _fetch_leagues_raw()
    seen_ids = set()
    national_leagues = []

    for l in data:
        league = l.get("league", {})
        typ = (league.get("type") or "").lower()
        if typ not in ["cup", "national"]:
            continue
        lid = league.get("id")
        country = l.get("country", {})
        name = league.get("name", "")
        country_name = country.get("name") or country.get("code") or ""

        if lid in seen_ids:
            continue
        seen_ids.add(lid)
        l["display_name"] = f"{name} ({country_name})" if country_name else name
        national_leagues.append(l)

    national_leagues.sort(key=lambda x: (x.get("country", {}).get("name") or "", x.get("league", {}).get("name") or ""))
    return national_leagues

# --------------------------
# Fixtures / partite
# --------------------------

def get_matches(league_id):
    """Recupera le partite di una lega, con fallback stagioni."""
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
# Ricerca squadre
# --------------------------

def search_teams(query):
    """
    Restituisce tutte le squadre che contengono la stringa `query`
    in tutte le leghe di club e nazionali.
    """
    results = []
    leagues = get_leagues() + get_national_teams()
    for l in leagues:
        matches = get_matches(l["league"]["id"])
        for m in matches:
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            if query.lower() in home.lower():
                results.append({"team": home, "match_id": m["fixture"]["id"], "league_id": l["league"]["id"]})
            if query.lower() in away.lower():
                results.append({"team": away, "match_id": m["fixture"]["id"], "league_id": l["league"]["id"]})
    return results
