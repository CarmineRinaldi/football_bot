from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.services.api_football import get_matches, generate_advanced_schedina
from app.db.session import SessionLocal
from app.db.models import User, Schedina
from app.config import VIP_MAX_MATCHES, DEFAULT_TIMEZONE
import pytz

scheduler = BackgroundScheduler()

def send_vip_schedine():
    db = SessionLocal()
    vip_users = db.query(User).filter(User.tier=="vip").all()
    for user in vip_users:
        # placeholder league
        league_id = user.chosen_league or "61"  # Serie A
        matches = get_matches(league_id)
        schedina = generate_advanced_schedina(matches, VIP_MAX_MATCHES)
        db_sched = Schedina(user_id=user.id, matches=schedina)
        db.add(db_sched)
        db.commit()
        # qui potresti inviare tramite bot
        print(f"Schedina inviata a {user.username} con {len(schedina)} partite")
    db.close()

def start_scheduler():
    scheduler.add_job(send_vip_schedine, 'cron', hour=9, timezone=DEFAULT_TIMEZONE)
    scheduler.start()
