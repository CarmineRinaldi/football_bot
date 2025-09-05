import os
import httpx

API_KEY = os.getenv("API_FOOTBALL_KEY")

async def get_matches(league_id: int):
    url = f"https://api-football.com/matches?league={league_id}"
    headers = {"X-API-KEY": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()
