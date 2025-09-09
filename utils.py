from datetime import datetime, timedelta
from config import FREE_MAX_MATCHES

async def can_use_free(last_free, free_max=FREE_MAX_MATCHES):
    if not last_free:
        return True
    delta = datetime.now() - last_free
    return delta >= timedelta(hours=24)

async def format_schedine(schedine):
    return "\n".join(f"- {s}" for s in schedine)

async def waiting_message():
    return "⏳ Attendere, sto preparando i dati..."
