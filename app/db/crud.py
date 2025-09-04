from sqlalchemy.orm import Session
from app.db import models


def get_user_by_tg(db: Session, tg_id: int):
return db.query(models.User).filter(models.User.tg_id == tg_id).first()


def create_user(db: Session, tg_id: int, username: str = None):
user = models.User(tg_id=tg_id, username=username)
db.add(user)
db.commit()
db.refresh(user)
return user


def upsert_user(db: Session, tg_id: int, username: str = None):
u = get_user_by_tg(db, tg_id)
if u:
if username and u.username != username:
u.username = username
db.commit()
db.refresh(u)
return u
return create_user(db, tg_id, username)


def set_user_tier(db: Session, user: models.User, tier: str):
user.tier = tier
db.commit()
db.refresh(user)
return user


def add_credits(db: Session, user: models.User, amount: int):
user.credits = (user.credits or 0) + int(amount)
db.commit()
db.refresh(user)
return user
