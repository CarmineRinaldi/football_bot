from datetime import datetime, timedelta
from typing import List, Optional


def can_use_free(last_free: Optional[datetime], free_max: int = 5) -> bool:
    """
    Controlla se l'utente può ancora usare il piano free.
    Ritorna True se sono passate almeno 24 ore dall'ultimo utilizzo.
    """
    if not last_free:
        return True
    delta = datetime.now() - last_free
    return delta >= timedelta(hours=24)


def format_schedine(schedine: List[str]) -> str:
    """
    Restituisce le schedine formattate come elenco leggibile.
    """
    return "\n".join(f"- {s}" for s in schedine)


def waiting_message() -> str:
    """
    Messaggio di attesa mostrato mentre il bot elabora.
    """
    return "⏳ Attendere, sto preparando i dati..."
