from datetime import datetime, timedelta

def can_use_free(last_free, free_max=5):
    if not last_free:
        return True
    delta = datetime.now() - last_free
    return delta >= timedelta(hours=24)

def format_schedine(schedine):
    return "\n".join(f"- {s}" for s in schedine)

def waiting_message():
    return "⏳ Attendere, sto preparando i dati..."
