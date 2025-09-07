import os
import requests
import json
import random

API_KEY = os.environ.get("API_FOOTBALL_KEY")
CACHE_FILE = "data/matches_cache.json"

def get_daily_matches():
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        # Simulazione match se non presente cache
        matches = [
            "Inter vs Milan 2-1",
            "Juventus vs Napoli 1-1",
            "Roma vs Lazio 3-0"
        ]
        with open(CACHE_FILE, "w") as f:
            json.dump(matches, f)
        return matches

def get_random_ticket():
    matches = get_daily_matches()
    return random.choice(matches)
