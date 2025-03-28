import unittest
import os
from datetime import datetime
from dotenv import load_dotenv

from database import create_database, init_db, get_db, DatabaseService
from database.models import InstagramAccount, Follower, ScrapingSession

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        load_dotenv()
        
        # Use test database
        os.environ['DB_NAME'] = 'instagram_scraper_test'
        
        # Create and initialize test database
        create_database()
        init_db()
        
        # Get database session
        cls.db = next(get_db())
        cls.db_service = DatabaseService(cls.db)

    def setUp(self):
        """Clear all tables before each test."""
        self.db.query(Follower).delete()
        self.db.query(ScrapingSession).delete()
        self.db.query(InstagramAccount).delete()
        self.db.commit()

    def test_create_account(self):
        """Test creating an Instagram account."""
        account = self.db_service.create_or_update_account(
            username='testuser',
            full_name='Test User',
            biography='Test bio',
            followers_count=100,
            following_count=50,
            is_private=False,
            is_verified=False
        )
        
        self.assertEqual(account.username, 'testuser')
        self.assertEqual(account.full_name, 'Test User')
        self.assertEqual(account.followers_count, 100)

    def test_create_follower(self):
        """Test creating a follower."""
        # Create account first
        account = self.db_service.create_or_update_account(
            username='testuser'
        )
        
        # Create follower
        follower = self.db_service.create_or_update_follower(
            account_id=account.id,
            username='follower1',
            full_name='Test Follower',
            is_private=False,
            is_business_account=True,
            business_category='Test Category'
        )
        
        self.assertEqual(follower.username, 'follower1')
        self.assertEqual(follower.full_name, 'Test Follower')
        self.assertTrue(follower.is_business_account)

    def test_scraping_session(self):
        """Test creating and updating a scraping session."""
        # Create account first
        account = self.db_service.create_or_update_account(
            username='testuser'
        )
        
        # Create session
        session = self.db_service.create_scraping_session(account.id)
        self.assertEqual(session.status, 'running')
        
        # Update session
        updated_session = self.db_service.complete_scraping_session(
            session.id,
            status='completed'
        )
        
        self.assertEqual(updated_session.status, 'completed')
        self.assertIsNotNone(updated_session.end_time)

    def test_get_account_stats(self):
        """Test getting account statistics."""
        # Create account
        account = self.db_service.create_or_update_account(
            username='testuser'
        )
        
        # Create followers
        for i in range(5):
            self.db_service.create_or_update_follower(
                account_id=account.id,
                username=f'follower{i}',
                is_business_account=(i % 2 == 0)  # Every other follower is a business
            )
        
        # Get stats
        stats = self.db_service.get_account_stats(account.id)
        
        self.assertEqual(stats['username'], 'testuser')
        self.assertEqual(stats['total_followers_scraped'], 5)
        self.assertEqual(stats['business_accounts'], 3)  # 3 business accounts (0, 2, 4)

    def test_get_followers_pagination(self):
        """Test follower pagination."""
        # Create account
        account = self.db_service.create_or_update_account(
            username='testuser'
        )
        
        # Create 15 followers
        for i in range(15):
            self.db_service.create_or_update_follower(
                account_id=account.id,
                username=f'follower{i}'
            )
        
        # Test pagination
        first_page = self.db_service.get_followers(account.id, limit=10, offset=0)
        second_page = self.db_service.get_followers(account.id, limit=10, offset=10)
        
        self.assertEqual(len(first_page), 10)
        self.assertEqual(len(second_page), 5)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        cls.db.close()

if __name__ == '__main__':
    unittest.main() 