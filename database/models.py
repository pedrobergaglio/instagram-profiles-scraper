from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    biography = Column(String(1000))
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    external_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    followers = relationship("Follower", back_populates="account")
    scraping_sessions = relationship("ScrapingSession", back_populates="account")

class Follower(Base):
    __tablename__ = 'followers'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('instagram_accounts.id'))
    scraping_session_id = Column(Integer, ForeignKey('scraping_sessions.id'))
    username = Column(String(255), nullable=False)
    full_name = Column(String(255))
    biography = Column(String(1000))
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    external_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    business_category = Column(String(255))
    is_business_account = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_score = Column(Float)  # Score from AI filtering
    ai_notes = Column(String(1000))  # Notes from AI analysis
    extra_data = Column(JSON)  # Additional metadata
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="followers")
    session = relationship("ScrapingSession", back_populates="followers")

class ScrapingSession(Base):
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True)
    target_username = Column(String(255), nullable=False)
    account_id = Column(Integer, ForeignKey('instagram_accounts.id'))
    status = Column(String(50), default='pending')  # pending, running, completed, failed, stopped
    max_followers = Column(Integer, default=1000)
    followers_scraped = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    last_cursor = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="scraping_sessions")
    followers = relationship("Follower", back_populates="session")