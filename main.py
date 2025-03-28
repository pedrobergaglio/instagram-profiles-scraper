import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Generator
from dotenv import load_dotenv

from database import get_db, DatabaseService
from session_manager import SessionManager
from proxy_manager import ProxyManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.session_manager = SessionManager()
        self.proxy_manager = ProxyManager()
        self.db = next(get_db())
        self.db_service = DatabaseService(self.db)

    def get_valid_session(self) -> Any:
        """Get a valid Instagram session."""
        session = self.session_manager.get_best_session()
        if not session:
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')
            if not username or not password:
                raise ValueError("Instagram credentials not found in environment variables")
            
            proxy = self.proxy_manager.get_next_proxy()
            session = self.session_manager.create_session(
                username=username,
                password=password,
                proxy=proxy
            )
        return session

    def scrape_account(self, target_username: str) -> Dict[str, Any]:
        """Scrape an Instagram account and its followers."""
        session = self.get_valid_session()
        
        try:
            # Get account info
            account_info = session.get_account_info(target_username)
            account = self.db_service.create_or_update_account(
                username=target_username,
                **account_info
            )
            
            # Create scraping session
            scraping_session = self.db_service.create_scraping_session(account.id)
            
            try:
                # Get followers
                for batch in self.get_detailed_follower_data(session, target_username):
                    for follower_data in batch:
                        self.db_service.create_or_update_follower(
                            account_id=account.id,
                            **follower_data
                        )
                        scraping_session.total_followers_scraped += 1
                
                self.db_service.complete_scraping_session(
                    scraping_session.id,
                    status='completed'
                )
                
            except Exception as e:
                logger.error(f"Error while scraping followers: {str(e)}")
                self.db_service.complete_scraping_session(
                    scraping_session.id,
                    status='failed'
                )
                raise
            
            return self.db_service.get_account_stats(account.id)
            
        except Exception as e:
            logger.error(f"Error while scraping account {target_username}: {str(e)}")
            raise

    def get_detailed_follower_data(
        self,
        session: Any,
        username: str,
        batch_size: int = 10
    ) -> Generator[list, None, None]:
        """Get detailed data for each follower in batches."""
        try:
            followers = []
            batch = []
            
            for follower in session.get_followers(username):
                try:
                    # Get detailed info for the follower
                    follower_info = session.get_account_info(follower['username'])
                    batch.append(follower_info)
                    
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                        
                    # Handle rate limits
                    self.handle_rate_limit(session)
                    
                except Exception as e:
                    logger.error(f"Error getting follower data for {follower['username']}: {str(e)}")
                    continue
            
            # Yield remaining followers
            if batch:
                yield batch
                
        except Exception as e:
            logger.error(f"Error in get_detailed_follower_data: {str(e)}")
            raise

    def handle_rate_limit(
        self,
        session: Any,
        error: Optional[Exception] = None,
        cooldown: int = 600
    ) -> None:
        """Handle rate limiting and challenges."""
        if error and "challenge_required" in str(error):
            self.session_manager.increment_challenges(session)
            if not self.session_manager.is_session_valid(session):
                session = self.get_valid_session()
        
        self.session_manager.increment_requests(session)
        self.session_manager.save_session(session)

def main():
    try:
        target_username = os.getenv('TARGET_USERNAME')
        if not target_username:
            raise ValueError("TARGET_USERNAME not found in environment variables")
        
        scraper = InstagramScraper()
        stats = scraper.scrape_account(target_username)
        
        logger.info("Scraping completed successfully!")
        logger.info(f"Stats for {target_username}:")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()