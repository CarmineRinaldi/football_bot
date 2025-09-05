from __future__ import annotations
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple

def main_menu_kb() -> InlineKeyboardMarkup:
    btns = [
        [InlineKeyboardButton(text="🏆 Campionati", callback_data="menu:leagues:0")],
        [InlineKeyboardButton(text="🧾 Le mie schedine", callback_data="menu:my_slips")],
        [InlineKeyboardButton(text="💳 Piani & Prezzi", callback_data="menu:plans")],
        [InlineKeyboardButton(text="ℹ️ Stato account", callback_data="menu:account")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=btns)

def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:main")]])

def leagues_kb(leagues: List[Tuple[int, str]], page: int, page_size: int = 8) -> InlineKeyboardMarkup:
    start = page * page_size
    chunk = leagues[start:start + page_size]
    rows = [[InlineKeyboardButton(text=label, callback_data=f"league:{lid}:fixtures:0")] for lid, label in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"menu:leagues:{page-1}"))
    if start + page_size < len(leagues):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"menu:leagues:{page+1}"))
    rows.append(nav or [InlineKeyboardButton(text="—", callback_data="noop")])
    rows.append([InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fixtures_kb(fixtures: List[Tuple[int, str]], league_id: int, page: int, page_size: int = 8) -> InlineKeyboardMarkup:
    start = page * page_size
    chunk = fixtures[start:start + page_size]
    rows = [[InlineKeyboardButton(text=label, callback_data=f"fixture:{fid}:markets")] for fid, label in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"league:{league_id}:fixtures:{page-1}"))
    if start + page_size < len(fixtures):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"league:{league_id}:fixtures:{page+1}"))
    rows.append(nav or [InlineKeyboardButton(text="—", callback_data="noop")])
    rows.append([InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:leagues:0")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def markets_kb(fixture_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1X2", callback_data=f"market:{fixture_id}:1x2")],
        [InlineKeyboardButton(text="🧺 Vedi schedina", callback_data="slip:view")],
        [InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:leagues:0")],
    ])

def picks_1x2_kb(fixture_id: int, odds: dict) -> InlineKeyboardMarkup:
    rows = [[
        InlineKeyboardButton(text=f"1 ({odds.get('1','-')})", callback_data=f"pick:{fixture_id}:1x2:1"),
        InlineKeyboardButton(text=f"X ({odds.get('X','-')})", callback_data=f"pick:{fixture_id}:1x2:X"),
        InlineKeyboardButton(text=f"2 ({odds.get('2','-')})", callback_data=f"pick:{fixture_id}:1x2:2"),
    ]]
    rows.append([InlineKeyboardButton(text="🧺 Vedi schedina", callback_data="slip:view")])
    rows.append([InlineKeyboardButton(text="⬅️ Indietro", callback_data=f"fixture:{fixture_id}:markets")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def slip_actions_kb(can_save: bool) -> InlineKeyboardMarkup:
    rows = []
    if can_save:
        rows.append([InlineKeyboardButton(text="💾 Salva schedina", callback_data="slip:save")])
    rows.append([InlineKeyboardButton(text="🧹 Svuota", callback_data="slip:clear")])
    rows.append([InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def plans_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟️ Pack 10 schedine – 2€", callback_data="buy:pack")],
        [InlineKeyboardButton(text="⭐ VIP – 4,99€/mese", callback_data="buy:vip")],
        [InlineKeyboardButton(text="⬅️ Indietro", callback_data="menu:main")],
    ])
