import os
import requests
from datetime import datetime

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY, "X-Auth-Token": API_KEY}

def _fetch_leagues_raw():
    try:
        res = requests.get(f"{BASE_URL}/leagues", headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.json().get("response", [])
    except Exception as e:
        print("Errore fetch leagues:", e)
        return []

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
