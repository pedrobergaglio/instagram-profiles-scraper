import threading
import queue
import time
from typing import List, Dict, Any
from database.models import InstagramAccount, Follower, ScrapingSession
from sqlalchemy.orm import Session
from .session_manager import SessionManager
import logging

logger = logging.getLogger(__name__)

class ScrapeWorker(threading.Thread):
    def __init__(
        self,
        task_queue: queue.Queue,
        result_queue: queue.Queue,
        db: Session,
        session_manager: SessionManager,
        batch_size: int = 50,
        delay: int = 2
    ):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.db = db
        self.session_manager = session_manager
        self.batch_size = batch_size
        self.delay = delay
        self.running = True

    def run(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break

                target_username = task["target_username"]
                session_id = task["session_id"]
                cursor = task.get("cursor")

                try:
                    # Get a valid Instagram session
                    insta_session = self.session_manager.get_best_session()
                    if not insta_session:
                        logger.error(f"No valid session available for {target_username}")
                        continue

                    # Fetch followers
                    followers_data = self._fetch_followers(
                        insta_session,
                        target_username,
                        cursor,
                        self.batch_size
                    )

                    # Process results
                    if followers_data:
                        self.result_queue.put({
                            "success": True,
                            "session_id": session_id,
                            "data": followers_data,
                            "next_cursor": followers_data.get("next_cursor")
                        })
                    
                    # Add delay between requests
                    time.sleep(self.delay)

                except Exception as e:
                    logger.error(f"Error processing task: {str(e)}")
                    self.result_queue.put({
                        "success": False,
                        "session_id": session_id,
                        "error": str(e)
                    })
                    self.session_manager.increment_challenges(insta_session)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                continue

    def _fetch_followers(
        self,
        session: Any,
        username: str,
        cursor: str = None,
        limit: int = 50
    ) -> Dict:
        """Fetch followers for a given username using the provided session."""
        try:
            # Use session to fetch followers
            # This is a placeholder - implement actual Instagram API call
            followers = []  # TODO: Implement actual follower fetching
            next_cursor = None  # TODO: Get next cursor from response

            return {
                "followers": followers,
                "next_cursor": next_cursor
            }

        except Exception as e:
            logger.error(f"Error fetching followers: {str(e)}")
            raise

    def stop(self):
        """Stop the worker thread."""
        self.running = False

class WorkerPool:
    def __init__(
        self,
        num_workers: int,
        db: Session,
        session_manager: SessionManager,
        batch_size: int = 50,
        delay: int = 2
    ):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers: List[ScrapeWorker] = []
        self.num_workers = num_workers
        self.db = db
        self.session_manager = session_manager
        self.batch_size = batch_size
        self.delay = delay

    def start(self):
        """Start the worker pool."""
        for _ in range(self.num_workers):
            worker = ScrapeWorker(
                self.task_queue,
                self.result_queue,
                self.db,
                self.session_manager,
                self.batch_size,
                self.delay
            )
            worker.start()
            self.workers.append(worker)

    def stop(self):
        """Stop all workers in the pool."""
        # Send stop signal to all workers
        for _ in range(self.num_workers):
            self.task_queue.put(None)

        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()

        self.workers = []

    def add_task(self, task: Dict):
        """Add a task to the queue."""
        self.task_queue.put(task)

    def get_result(self, timeout: int = 1) -> Dict:
        """Get a result from the queue."""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None 