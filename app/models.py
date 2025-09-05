from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class Selection:
    fixture_id: int
    league_id: int
    home: str
    away: str
    market: str     # "1x2"
    pick: str       # "1" | "X" | "2"
    odd: float

@dataclass
class Slip:
    items: List[Selection]
    combined_odds: float
