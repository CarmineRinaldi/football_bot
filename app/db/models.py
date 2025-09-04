from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
__tablename__ = "users"
id = Column(Integer, primary_key=True, index=True)
tg_id = Column(Integer, unique=True, index=True, nullable=False)
username = Column(String, nullable=True)
tier = Column(String, default="free")
free_league = Column(String, nullable=True)
credits = Column(Integer, default=0) # per pack 2€
vip_daily_enabled = Column(Boolean, default=False)
vip_daily_time = Column(String, default="09:00")
timezone = Column(String, default="Europe/Rome")
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Subscription(Base):
__tablename__ = "subscriptions"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
stripe_customer_id = Column(String, nullable=True)
stripe_sub_id = Column(String, nullable=True)
status = Column(String, nullable=True)
current_period_end = Column(Integer, nullable=True)


class Payment(Base):
__tablename__ = "payments"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
kind = Column(String) # oneoff|sub
stripe_id = Column(String)
amount = Column(Integer)
currency = Column(String)
status = Column(String)
meta = Column(JSON, nullable=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScheduledJob(Base):
__tablename__ = "scheduled_jobs"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
when_at = Column(DateTime(timezone=True), nullable=False)
payload = Column(JSON)
status = Column(String, default="pending")
