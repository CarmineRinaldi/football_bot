import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bot_logic import start, show_main_menu, show_leagues, show_matches, create_ticket
from db import add_user, get_user_plan, get_user_tickets, delete_old_tickets
from football_api import get_leagues, get_matches
from stripe_webhook import handle_stripe_event  # import corretto dal tuo file

app = FastAPI()


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    response = handle_stripe_event(payload, sig_header)
    return JSONResponse(content=response)


@app.post("/bot/start")
async def bot_start(update: dict):
    return JSONResponse(content=start(update))


@app.post("/bot/main_menu")
async def bot_main_menu(update: dict):
    return JSONResponse(content=show_main_menu(update))


@app.post("/bot/leagues")
async def bot_leagues(update: dict):
    leagues = get_leagues()
    return JSONResponse(content=show_leagues(update, leagues))


@app.post("/bot/matches")
async def bot_matches(update: dict):
    league_id = update.get("league_id")
    matches = get_matches(league_id)
    return JSONResponse(content=show_matches(update, matches))


@app.post("/bot/create_ticket")
async def bot_create_ticket(update: dict):
    return JSONResponse(content=create_ticket(update))
