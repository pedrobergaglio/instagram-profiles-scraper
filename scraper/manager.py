from typing import Optional, Dict, List, Generator, Any
from sqlalchemy.orm import Session
from database.models import InstagramAccount, Follower, ScrapingSession
from .worker import WorkerPool
from .session_manager import SessionManager
from .proxy_manager import ProxyManager
import logging
from datetime import datetime
import json
import time
import threading
from queue import Queue
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ScraperManager:
    def __init__(self, db, username=None, password=None, batch_size=50, delay=2):
        self.db = db
        self.username = username or os.getenv('INSTAGRAM_USERNAME')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD')
        self.batch_size = batch_size
        self.delay = delay
        self.results_queue = Queue()
        self.session_manager = SessionManager()
        self.proxy_manager = ProxyManager()
        self.worker_pool = WorkerPool(
            num_workers=3,
            db=db,
            session_manager=self.session_manager,
            batch_size=batch_size,
            delay=delay
        )
        self.active_sessions = {}
        logger.info(f"Initialized ScraperManager with batch_size={batch_size}, delay={delay}")

    def get_valid_session(self) -> Any:
        """Get a valid Instagram session."""
        logger.info("Attempting to get valid Instagram session")
        session = self.session_manager.get_best_session()
        
        if not session:
            logger.info("No valid session found, creating new session")
            if not self.username or not self.password:
                error_msg = "Instagram credentials not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            proxy = self.proxy_manager.get_next_proxy()
            logger.info(f"Creating new session with proxy: {proxy}")
            
            try:
                session = self.session_manager.create_session(
                    username=self.username,
                    password=self.password,
                    proxy=proxy
                )
                logger.info("Successfully created new Instagram session")
            except Exception as e:
                logger.error(f"Failed to create session: {str(e)}")
                raise
        
        return session

    def start_scraping(self, target_username: str, max_followers: int = 1000) -> Optional[int]:
        """Start a new scraping session."""
        try:
            logger.info(f"Starting scraping process for @{target_username}")
            session = self.get_valid_session()
            
            # Get account info
            logger.info(f"Fetching account info for @{target_username}")
            try:
                account_info = session.get_account_info(target_username)
                logger.info(f"Successfully fetched account info for @{target_username}")
            except Exception as e:
                logger.error(f"Failed to fetch account info: {str(e)}")
                raise

            # Create or update account
            account = self.db.query(InstagramAccount).filter_by(username=target_username).first()
            if not account:
                account = InstagramAccount(
                    username=target_username,
                    full_name=account_info.get('full_name'),
                    biography=account_info.get('biography'),
                    follower_count=account_info.get('follower_count', 0),
                    following_count=account_info.get('following_count', 0),
                    post_count=account_info.get('post_count', 0),
                    is_private=account_info.get('is_private', False),
                    is_verified=account_info.get('is_verified', False),
                    external_url=account_info.get('external_url'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(account)
                logger.info(f"Created new account record for @{target_username}")
            else:
                # Update existing account
                for key, value in account_info.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                account.updated_at = datetime.utcnow()
                logger.info(f"Updated existing account record for @{target_username}")
            
            self.db.commit()

            # Create scraping session
            session_record = ScrapingSession(
                target_username=target_username,
                account_id=account.id,
                status="running",
                max_followers=max_followers,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(session_record)
            self.db.commit()
            
            logger.info(f"Started scraping session #{session_record.id} for @{target_username}")

            # Start the scraping process in background
            self.active_sessions[session_record.id] = {
                "session": session,
                "cursor": None,
                "followers_scraped": 0,
                "max_followers": max_followers,
                "errors": 0,
                "last_request": datetime.utcnow()
            }

            # Start processing followers
            threading.Thread(
                target=self._process_followers,
                args=(session_record.id, target_username),
                daemon=True
            ).start()

            return session_record.id

        except Exception as e:
            logger.error(f"Error starting scraping session: {str(e)}")
            return None

    def _process_followers(self, session_id: int, username: str):
        """Process followers in background."""
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                logger.error(f"No session data found for session #{session_id}")
                return

            instagram_session = session_data["session"]
            batch = []
            
            logger.info(f"Starting follower processing for session #{session_id}")
            
            for follower in instagram_session.get_followers(username):
                try:
                    if len(batch) >= self.batch_size:
                        self.add_result(session_id, batch)
                        batch = []
                        time.sleep(self.delay)  # Rate limiting
                    
                    # Get detailed follower info
                    follower_info = instagram_session.get_account_info(follower['username'])
                    batch.append(follower_info)
                    
                    # Handle rate limits and challenges
                    self.handle_rate_limit(instagram_session)
                    
                except Exception as e:
                    logger.error(f"Error processing follower {follower['username']}: {str(e)}")
                    self.handle_rate_limit(instagram_session, error=e)
                    continue
            
            # Add remaining followers
            if batch:
                self.add_result(session_id, batch)
            
            logger.info(f"Completed follower processing for session #{session_id}")
            
        except Exception as e:
            logger.error(f"Error in follower processing thread: {str(e)}")
            self._handle_scraping_error(session_id, str(e))

    def handle_rate_limit(self, session: Any, error: Optional[Exception] = None, cooldown: int = 600):
        """Handle rate limiting and challenges."""
        try:
            if error and "challenge_required" in str(error):
                logger.warning(f"Challenge required for session, attempting to resolve")
                try:
                    # Try to resolve challenge
                    session._login()  # This will trigger challenge resolution
                    logger.info("Successfully resolved challenge")
                    return
                except Exception as ce:
                    logger.error(f"Failed to resolve challenge: {str(ce)}")
                    self.session_manager.increment_challenges(session)
                    
                    # Get a new session if this one has too many challenges
                    if not self.session_manager.is_session_valid(session):
                        logger.info("Session no longer valid, getting new session")
                        session = self.get_valid_session()
            
            # Handle rate limits
            if error and ("rate limit" in str(error).lower() or "too many requests" in str(error).lower()):
                logger.warning(f"Rate limit hit, cooling down for {cooldown} seconds")
                time.sleep(cooldown)
            
            # Always increment requests and save session state
            self.session_manager.increment_requests(session)
            # Find username for the session
            for username, data in self.session_manager.sessions.items():
                if data["session"] == session:
                    self.session_manager.save_session(username, session)
                    break
            
            # Add delay between requests
            time.sleep(self.delay)
        except Exception as e:
            logger.error(f"Error handling rate limit: {str(e)}")

    def _handle_scraping_error(self, session_id: int, error_message: str):
        """Handle scraping errors."""
        try:
            session_record = self.db.get(ScrapingSession, session_id)
            if session_record:
                session_record.error_count += 1
                session_record.last_error = error_message
                session_record.status = "failed" if session_record.error_count >= 3 else "running"
                session_record.updated_at = datetime.utcnow()
                self.db.commit()
                logger.error(f"Updated session #{session_id} with error: {error_message}")
        except Exception as e:
            logger.error(f"Error handling scraping error: {str(e)}")

    def process_results(self):
        """Process scraping results from the queue."""
        try:
            # Process any pending results
            while not self.results_queue.empty():
                result = self.results_queue.get()
                session_id = result.get("session_id")
                followers = result.get("followers", [])
                
                session = self.db.get(ScrapingSession, session_id)  # Using newer Session.get() syntax
                if session:
                    for follower_data in followers:
                        follower = Follower(
                            username=follower_data["username"],
                            full_name=follower_data.get("full_name"),
                            follower_count=follower_data.get("follower_count", 0),
                            following_count=follower_data.get("following_count", 0),
                            post_count=follower_data.get("post_count", 0),
                            is_private=follower_data.get("is_private", False),
                            is_verified=follower_data.get("is_verified", False),
                            account_id=session.account_id,
                            scraping_session_id=session.id,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        self.db.add(follower)
                    
                    session.followers_scraped += len(followers)
                    session.updated_at = datetime.utcnow()
                    
                    if session.followers_scraped >= session.max_followers:
                        session.status = "completed"
                        session.completed_at = datetime.utcnow()
                        logger.info(f"Session #{session_id} completed successfully")
                    
                    self.db.commit()
                    logger.debug(f"Processed {len(followers)} followers for session #{session_id}")
        except Exception as e:
            logger.error(f"Error processing results: {str(e)}")

    def add_result(self, session_id, followers):
        """Add scraping results to the queue."""
        self.results_queue.put({
            "session_id": session_id,
            "followers": followers
        })
        logger.debug(f"Added {len(followers)} followers to queue for session #{session_id}")

    def stop_scraping(self, session_id):
        """Stop a specific scraping session."""
        try:
            session = self.db.get(ScrapingSession, session_id)  # Using newer Session.get() syntax
            if session:
                session.status = "stopped"
                session.updated_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"Stopped scraping session #{session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping session #{session_id}: {str(e)}")
            return False

    def stop_all(self):
        """Stop all running scraping sessions."""
        try:
            running_sessions = self.db.query(ScrapingSession).filter_by(status="running").all()
            for session in running_sessions:
                session.status = "stopped"
                session.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Stopped all running sessions ({len(running_sessions)} sessions)")
            return True
        except Exception as e:
            logger.error(f"Error stopping all sessions: {str(e)}")
            return False

    def get_session_status(self, session_id):
        """Get the current status of a scraping session."""
        try:
            session = self.db.get(ScrapingSession, session_id)  # Using newer Session.get() syntax
            if not session:
                logger.warning(f"Session #{session_id} not found")
                return None

            return {
                "id": session.id,
                "target_username": session.target_username,
                "status": session.status,
                "followers_scraped": session.followers_scraped,
                "max_followers": session.max_followers,
                "error_count": session.error_count,
                "last_error": session.last_error,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
        except Exception as e:
            logger.error(f"Error getting status for session #{session_id}: {str(e)}")
            return None 