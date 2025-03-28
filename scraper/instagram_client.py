from instagram_private_api import Client, ClientCompatPatch
from instagram_private_api.errors import ClientError
import time
import logging
from typing import Generator, Dict, Any

logger = logging.getLogger(__name__)

class InstagramClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client(
            username, 
            password,
            auto_patch=True,
            drop_incompat_keys=False
        )

    def _login(self):
        """Login to Instagram."""
        try:
            # Perform new login
            self.client.login()
            logger.info(f"Successfully logged in as {self.username}")
            
        except ClientError as e:
            if "challenge_required" in str(e):
                logger.warning(f"Challenge required for {self.username}")
                try:
                    # Get challenge choices
                    challenge = self.client.challenge_resolve(self.client.last_json.get("challenge", {}).get("api_path"))
                    if challenge.get("step_name") == "select_verify_method":
                        # Choose email verification by default
                        challenge = self.client.challenge_resolve(challenge["step_data"]["choice"])
                        if challenge.get("step_name") == "verify_email":
                            # Wait for user to enter code
                            logger.info("Please check your email for verification code")
                            time.sleep(30)  # Give user time to check email
                            # Try to verify with empty code first (in case user already entered it)
                            challenge = self.client.challenge_resolve("")
                            if challenge.get("step_name") == "verify_email":
                                logger.error("Email verification failed")
                                raise
                    logger.info("Challenge resolved successfully")
                except Exception as ce:
                    logger.error(f"Failed to resolve challenge: {str(ce)}")
                    raise
            else:
                logger.error(f"Failed to login: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            raise

    def get_followers(self, username: str) -> Generator[Dict[str, Any], None, None]:
        """Get followers of an Instagram account."""
        try:
            # Get user info first
            user_info = self.client.username_info(username)
            user_id = user_info['user']['pk']
            rank_token = self.client.generate_uuid()
            followers = []
            next_max_id = None
            retry_count = 0
            max_retries = 3
            
            while True:
                try:
                    # Get followers with pagination
                    results = self.client.user_followers(
                        user_id, 
                        rank_token=rank_token,
                        max_id=next_max_id
                    )
                    
                    if not results.get('users', []):
                        break
                        
                    for user in results.get('users', []):
                        try:
                            # Get detailed user info
                            user_info = self.client.user_info(user['pk'])
                            if not user_info or 'user' not in user_info:
                                logger.warning(f"Invalid user info response for user {user.get('pk')}")
                                continue

                            user_data = user_info['user']
                            yield {
                                "username": user_data.get('username', ''),
                                "full_name": user_data.get('full_name', ''),
                                "biography": user_data.get('biography', ''),
                                "follower_count": user_data.get('follower_count', 0),
                                "following_count": user_data.get('following_count', 0),
                                "post_count": user_data.get('media_count', 0),
                                "is_private": user_data.get('is_private', False),
                                "is_verified": user_data.get('is_verified', False),
                                "external_url": user_data.get('external_url', '')
                            }
                            time.sleep(2)  # Rate limiting between user info requests
                            retry_count = 0  # Reset retry count on successful request
                            
                        except ClientError as e:
                            error_msg = str(e).lower()
                            if "challenge_required" in error_msg:
                                logger.warning(f"Challenge required while getting follower info")
                                self._login()  # Re-login to handle challenge
                                continue
                            elif "login_required" in error_msg:
                                logger.warning(f"Login required while getting follower info")
                                self._login()  # Re-login to handle expired session
                                continue
                            elif "please wait" in error_msg:
                                retry_count += 1
                                if retry_count >= max_retries:
                                    logger.error("Max retries reached, taking a longer break")
                                    time.sleep(300)  # 5 minute break
                                    retry_count = 0
                                else:
                                    wait_time = 60 * retry_count  # Exponential backoff
                                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                                    time.sleep(wait_time)
                                continue
                            else:
                                logger.error(f"Error getting follower info: {str(e)}")
                                continue
                        except KeyError as e:
                            logger.error(f"Missing field in user info response: {str(e)}")
                            continue
                        except Exception as e:
                            logger.error(f"Error getting follower info: {str(e)}")
                            continue
                    
                    next_max_id = results.get('next_max_id')
                    if not next_max_id:
                        break
                        
                    time.sleep(5)  # Rate limiting between follower page requests
                    
                except ClientError as e:
                    error_msg = str(e).lower()
                    if "challenge_required" in error_msg:
                        logger.warning(f"Challenge required while getting followers")
                        self._login()  # Re-login to handle challenge
                        continue
                    elif "login_required" in error_msg:
                        logger.warning(f"Login required while getting followers")
                        self._login()  # Re-login to handle expired session
                        continue
                    elif "please wait" in error_msg:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error("Max retries reached, taking a longer break")
                            time.sleep(300)  # 5 minute break
                            retry_count = 0
                        else:
                            wait_time = 60 * retry_count  # Exponential backoff
                            logger.warning(f"Rate limited, waiting {wait_time} seconds")
                            time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Error getting followers batch: {str(e)}")
                        break
                except Exception as e:
                    logger.error(f"Error getting followers batch: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Error getting followers for {username}: {str(e)}")
            raise

    def get_account_info(self, username: str) -> Dict[str, Any]:
        """Get information about an Instagram account."""
        try:
            user_info = self.client.username_info(username)
            if not user_info or 'user' not in user_info:
                raise ValueError(f"Invalid response for username {username}")
                
            user = user_info['user']
            return {
                "username": user.get('username', ''),
                "full_name": user.get('full_name', ''),
                "biography": user.get('biography', ''),
                "follower_count": user.get('follower_count', 0),
                "following_count": user.get('following_count', 0),
                "post_count": user.get('media_count', 0),
                "is_private": user.get('is_private', False),
                "is_verified": user.get('is_verified', False),
                "external_url": user.get('external_url', '')
            }
        except ClientError as e:
            if "challenge_required" in str(e):
                logger.warning(f"Challenge required while getting account info for {username}")
                self._login()  # Re-login to handle challenge
                return self.get_account_info(username)  # Retry after re-login
            else:
                logger.error(f"Error getting account info for {username}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error getting account info for {username}: {str(e)}")
            raise

    def is_logged_in(self) -> bool:
        """Check if the client is logged in."""
        try:
            self.client.get_timeline_feed()
            return True
        except:
            return False