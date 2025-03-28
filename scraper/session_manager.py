from typing import Optional, Dict, Any
import time
import json
import os
import logging
from datetime import datetime, timedelta
import pickle
from pathlib import Path
from .instagram_client import InstagramClient

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, sessions_dir: str = "Insta Saved Sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions: Dict[str, Dict] = {}
        self.load_sessions()
        logger.info("Initialized SessionManager")

    def load_sessions(self):
        """Load all saved sessions from disk."""
        try:
            if not self.sessions_dir.exists():
                self.sessions_dir.mkdir(parents=True)
                return

            for file in self.sessions_dir.glob("*.pkl"):
                try:
                    username = file.stem
                    with open(file, 'rb') as f:
                        session_data = pickle.load(f)
                        if isinstance(session_data, InstagramClient) and session_data.is_logged_in():
                            self.sessions[username] = {
                                "session": session_data,
                                "last_used": datetime.now(),
                                "challenges": 0,
                                "requests": 0
                            }
                            logger.info(f"Loaded valid session for {username}")
                        else:
                            logger.warning(f"Invalid or expired session for {username}")
                except Exception as e:
                    logger.error(f"Error loading session {file}: {str(e)}")

        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")

    def create_session(self, username: str, password: str, proxy: Optional[str] = None) -> InstagramClient:
        """Create a new Instagram session."""
        try:
            client = InstagramClient(username, password)
            self.save_session(username, client)
            logger.info(f"Created new session for {username}")
            return client
        except Exception as e:
            logger.error(f"Error creating session for {username}: {str(e)}")
            raise

    def save_session(self, username: str, session_data: InstagramClient):
        """Save a session to disk."""
        try:
            file_path = self.sessions_dir / f"{username}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(session_data, f)

            self.sessions[username] = {
                "session": session_data,
                "last_used": datetime.now(),
                "challenges": 0,
                "requests": 0
            }
            logger.info(f"Saved session for {username}")

        except Exception as e:
            logger.error(f"Error saving session for {username}: {str(e)}")

    def get_best_session(self) -> Optional[InstagramClient]:
        """Get the best available session based on usage and challenges."""
        try:
            if not self.sessions:
                return None

            # Sort sessions by challenges and last used time
            valid_sessions = [
                (username, data) for username, data in self.sessions.items()
                if self.is_session_valid(username)
            ]

            if not valid_sessions:
                return None

            # Sort by challenges (ascending) and last used time (oldest first)
            valid_sessions.sort(
                key=lambda x: (x[1]["challenges"], x[1]["last_used"])
            )

            # Get the best session
            username, data = valid_sessions[0]
            data["last_used"] = datetime.now()
            data["requests"] += 1
            logger.info(f"Using session for {username}")
            return data["session"]

        except Exception as e:
            logger.error(f"Error getting best session: {str(e)}")
            return None

    def increment_challenges(self, session: InstagramClient):
        """Increment the challenge count for a session."""
        try:
            for username, data in self.sessions.items():
                if data["session"] == session:
                    data["challenges"] += 1
                    logger.info(f"Incremented challenges for {username} to {data['challenges']}")
                    break

        except Exception as e:
            logger.error(f"Error incrementing challenges: {str(e)}")

    def increment_requests(self, session: InstagramClient):
        """Increment the request count for a session."""
        try:
            for username, data in self.sessions.items():
                if data["session"] == session:
                    data["requests"] += 1
                    data["last_used"] = datetime.now()
                    break
        except Exception as e:
            logger.error(f"Error incrementing requests: {str(e)}")

    def is_session_valid(self, username: str) -> bool:
        """Check if a session is valid based on challenges and age."""
        try:
            data = self.sessions.get(username)
            if not data:
                return False

            # Check if session is too old (24 hours)
            session_age = datetime.now() - data["last_used"]
            if session_age > timedelta(hours=24):
                logger.warning(f"Session for {username} is too old")
                return False

            # Check if too many challenges
            if data["challenges"] >= 3:
                logger.warning(f"Session for {username} has too many challenges")
                return False

            # Verify session is still logged in
            if not isinstance(data["session"], InstagramClient) or not data["session"].is_logged_in():
                logger.warning(f"Session for {username} is no longer logged in")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking session validity: {str(e)}")
            return False

    def clear_challenges(self, username: str):
        """Reset the challenge count for a session."""
        try:
            if username in self.sessions:
                self.sessions[username]["challenges"] = 0
                logger.info(f"Cleared challenges for {username}")
        except Exception as e:
            logger.error(f"Error clearing challenges: {str(e)}")

    def get_session_stats(self) -> Dict:
        """Get statistics about all sessions."""
        return {
            "total_sessions": len(self.sessions),
            "valid_sessions": sum(1 for username in self.sessions if self.is_session_valid(username)),
            "total_challenges": sum(data["challenges"] for data in self.sessions.values()),
            "total_requests": sum(data["requests"] for data in self.sessions.values())
        } 