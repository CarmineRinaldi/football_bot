from __future__ import annotations
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from typing import Optional, List, Dict

async def wipe_and_send(bot: Bot, cq: Optional[CallbackQuery], chat_id: int, text: str, reply_markup=None) -> Message:
    """Cancella il messaggio precedente (se possibile) e invia il nuovo. Fallback: edit."""
    if cq and cq.message:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=cq.message.message_id)
            return await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)
        except Exception:
            try:
                return await bot.edit_message_text(text, chat_id, cq.message.message_id,
                                                   reply_markup=reply_markup, disable_web_page_preview=True)
            except Exception:
                pass
    return await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)

def format_selection(item: Dict) -> str:
    return f"• {item['home']} vs {item['away']} — {item['market']} {item['pick']} @ {item['odd']}"

def format_slip(items: List[Dict]) -> str:
    if not items:
        return "🧺 La tua schedina è vuota. Aggiungi partite dai Campionati."
    total = 1.0
    lines = []
    for it in items:
        try:
            total *= float(it.get("odd", 1.0))
        except Exception:
            pass
        lines.append(format_selection(it))
    lines.append("\n📈 Quota totale: {:.2f}".format(total))
    return "\n".join(lines)

def combined_odds(items: List[Dict]) -> float:
    c = 1.0
    for it in items:
        try:
            c *= float(it.get("odd", 1.0))
        except Exception:
            pass
    return round(c, 2)
