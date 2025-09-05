from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    tier = Column(String, default="free")  # free / pack / vip
    chosen_league = Column(String, nullable=True)
    timezone = Column(String, default="Europe/Rome")
    vip_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    credits = relationship("Credit", back_populates="user")
    schedines = relationship("Schedina", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")

class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    remaining = Column(Integer, default=0)
    
    user = relationship("User", back_populates="credits")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_subscription_id = Column(String)
    active = Column(Boolean, default=True)
    current_period_end = Column(DateTime)
    
    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    stripe_payment_id = Column(String)
    amount = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Schedina(Base):
    __tablename__ = "schedine"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    matches = Column(JSON)  # Lista partite con pronostici
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="schedines")

class LeagueCache(Base):
    __tablename__ = "leagues_cache"
    id = Column(Integer, primary_key=True)
    league_id = Column(String, unique=True)
    data = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)
