import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database.config import SessionLocal
from database.models import InstagramAccount, Follower, ScrapingSession
from datetime import datetime
from scraper.manager import ScraperManager

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_scraping_session(db_session):
    # Create a test account
    account = InstagramAccount(
        username="test_account",
        full_name="Test Account",
        follower_count=1000,
        following_count=500,
        post_count=100,
        is_private=False,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    db_session.commit()

    # Create a scraping session
    session = ScrapingSession(
        target_username="test_account",
        status="running",
        max_followers=100,
        followers_scraped=0,
        error_count=0,
        account_id=account.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Add some test followers
    followers = []
    for i in range(5):
        follower = Follower(
            username=f"follower_{i}",
            full_name=f"Follower {i}",
            follower_count=100 + i,
            following_count=50 + i,
            post_count=10 + i,
            is_private=False,
            is_verified=False,
            account_id=account.id,
            scraping_session_id=session.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        followers.append(follower)
    
    db_session.add_all(followers)
    db_session.commit()

    # Verify data
    assert db_session.query(InstagramAccount).count() == 1
    assert db_session.query(ScrapingSession).count() == 1
    assert db_session.query(Follower).count() == 5

    # Test ScraperManager
    manager = ScraperManager(db_session)
    session_status = manager.get_session_status(session.id)
    
    assert session_status["target_username"] == "test_account"
    assert session_status["status"] == "running"
    assert session_status["followers_scraped"] == 0

def test_query_followers(db_session):
    # Query followers with filters
    followers = db_session.query(Follower).filter(
        Follower.follower_count >= 102
    ).all()
    
    assert len(followers) == 3  # Should find followers 2, 3, and 4

def test_cleanup(db_session):
    # Clean up test data
    db_session.query(Follower).delete()
    db_session.query(ScrapingSession).delete()
    db_session.query(InstagramAccount).delete()
    db_session.commit() 