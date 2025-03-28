from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import InstagramAccount, Follower, ScrapingSession

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_account(self, username: str, **kwargs) -> InstagramAccount:
        """Create or update an Instagram account."""
        account = self.db.query(InstagramAccount).filter(InstagramAccount.username == username).first()
        
        if account:
            for key, value in kwargs.items():
                setattr(account, key, value)
            account.updated_at = datetime.utcnow()
        else:
            account = InstagramAccount(username=username, **kwargs)
            self.db.add(account)
        
        try:
            self.db.commit()
            self.db.refresh(account)
        except IntegrityError:
            self.db.rollback()
            raise
        
        return account

    def create_or_update_follower(self, account_id: int, username: str, **kwargs) -> Follower:
        """Create or update a follower."""
        follower = (
            self.db.query(Follower)
            .filter(
                Follower.account_id == account_id,
                Follower.username == username
            )
            .first()
        )
        
        if follower:
            for key, value in kwargs.items():
                setattr(follower, key, value)
            follower.updated_at = datetime.utcnow()
        else:
            follower = Follower(
                account_id=account_id,
                username=username,
                **kwargs
            )
            self.db.add(follower)
        
        try:
            self.db.commit()
            self.db.refresh(follower)
        except IntegrityError:
            self.db.rollback()
            raise
        
        return follower

    def create_scraping_session(self, account_id: int) -> ScrapingSession:
        """Create a new scraping session."""
        session = ScrapingSession(
            account_id=account_id,
            status='running',
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_scraping_session(self, session_id: int, **kwargs) -> ScrapingSession:
        """Update a scraping session."""
        session = self.db.query(ScrapingSession).filter(ScrapingSession.id == session_id).first()
        if not session:
            raise ValueError(f"No scraping session found with id {session_id}")
        
        for key, value in kwargs.items():
            setattr(session, key, value)
        
        self.db.commit()
        self.db.refresh(session)
        return session

    def complete_scraping_session(self, session_id: int, status: str = 'completed') -> ScrapingSession:
        """Mark a scraping session as complete."""
        return self.update_scraping_session(
            session_id,
            status=status,
            end_time=datetime.utcnow()
        )

    def get_account_by_username(self, username: str) -> Optional[InstagramAccount]:
        """Get an Instagram account by username."""
        return self.db.query(InstagramAccount).filter(InstagramAccount.username == username).first()

    def get_followers(self, account_id: int, limit: int = 100, offset: int = 0) -> List[Follower]:
        """Get followers for an account with pagination."""
        return (
            self.db.query(Follower)
            .filter(Follower.account_id == account_id)
            .order_by(Follower.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_active_scraping_sessions(self) -> List[ScrapingSession]:
        """Get all active scraping sessions."""
        return (
            self.db.query(ScrapingSession)
            .filter(ScrapingSession.status == 'running')
            .all()
        )

    def get_account_stats(self, account_id: int) -> Dict[str, Any]:
        """Get statistics for an account."""
        account = self.db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account:
            raise ValueError(f"No account found with id {account_id}")
        
        total_followers = self.db.query(Follower).filter(Follower.account_id == account_id).count()
        business_accounts = (
            self.db.query(Follower)
            .filter(
                Follower.account_id == account_id,
                Follower.is_business_account == True
            )
            .count()
        )
        
        return {
            'username': account.username,
            'total_followers_scraped': total_followers,
            'business_accounts': business_accounts,
            'last_updated': account.updated_at
        } 