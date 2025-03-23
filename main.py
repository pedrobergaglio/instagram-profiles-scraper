import os
import time
import random
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from instagpy import InstaGPy
from instagpy import config

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {timestamp} - {message}")

def save_to_csv(data, filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = data_dir / f"{filename}_{timestamp}.csv"
    df = pd.DataFrame([data] if isinstance(data, dict) else data)
    df.to_csv(filepath, index=False)
    log(f"Data saved to {filepath}")

def wait_with_backoff(attempt=1, base_delay=60):
    """Implement exponential backoff when rate limited"""
    delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
    max_delay = 900  # Max 15 minutes
    delay = min(delay, max_delay)
    log(f"Rate limit hit. Waiting {delay} seconds before retry (attempt {attempt})...")
    time.sleep(delay)

def handle_rate_limit(response):
    """Check if response indicates rate limiting"""
    if isinstance(response, dict):
        message = response.get('message', '').lower()
        if 'wait' in message or 'rate limit' in message:
            return True
    return False

def get_detailed_follower_data(insta, followers, max_followers=20):
    """Get detailed data for each public follower with batch processing"""
    detailed_followers = []
    processed = 0
    batch_size = 10  # Reduced batch size
    public_accounts = [f for f in followers if not f.get('is_private', True)]
    retry_count = 0
    max_retries = 5
    
    for i in range(0, len(public_accounts), batch_size):
        if processed >= max_followers:
            break
            
        # Process current batch
        batch = public_accounts[i:i + batch_size]
        batch_processed = 0
        
        for follower in batch:
            if processed >= max_followers:
                break
                
            try:
                username = follower.get('username')
                log(f"Fetching detailed data for public account: {username}")
                
                # Get detailed user data
                user_data = insta.get_user_data(username)
                
                if handle_rate_limit(user_data):
                    retry_count += 1
                    if retry_count > max_retries:
                        log("Max retries reached. Saving current progress...", "WARNING")
                        return detailed_followers
                    wait_with_backoff(retry_count)
                    continue
                
                if user_data and user_data.get('status') == 'ok':
                    detailed_followers.append(user_data.get('user', {}))
                    processed += 1
                    batch_processed += 1
                    retry_count = 0  # Reset counter on success
                
                # Random delay between requests
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                log(f"Error fetching data for {username}: {e}", "ERROR")
                if 'wait' in str(e).lower():
                    retry_count += 1
                    wait_with_backoff(retry_count)
                continue
        
        log(f"Processed batch of {batch_processed} public accounts. Total processed: {processed}")
        # Longer sleep between batches
        sleep_time = random.uniform(30, 60)
        log(f"Sleeping for {sleep_time:.2f} seconds between batches...")
        time.sleep(sleep_time)
            
    return detailed_followers

def main():

    # Load environment variables and create data directory
    load_dotenv(override=True)

    config.MAX_RETRIES = 3
    config.TIMEOUT = 10
    
    log("Starting Instagram scraper...")
    
    # Initialize InstaGPy
    insta = InstaGPy(
        use_mutiple_account=False,
        session_ids=None,
        min_requests=3,
        max_requests=6
    )
    
    try:
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        target_username = os.getenv('TARGET_USERNAME', 'instagram')
        
        if not username or not password:
            raise ValueError("Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file")
        
        log(f"Attempting to login as {username}...")
        
        # Login with credentials
        insta.login(
            username=username, 
            password=password, 
            save_session=True
        )
        
        if not insta.logged_in:
            raise Exception("Failed to login")
        
        log("Successfully logged in!")
        
        # Get user data with one API call
        log(f"Fetching data for target user: {target_username}")
        user_data = insta.get_user_data(target_username)
        save_to_csv(user_data, 'user_details')
        
        # Add delay before next request
        time.sleep(random.uniform(2, 15))
        
        # Get followers if account is public
        if not user_data.get('user', {}).get('is_private'):
            log("Account is public, fetching followers...")
            followers = []
            retry_count = 0
            
            while retry_count < 2:  # Max 5 retries for initial follower fetch
                try:
                    response = insta.get_user_friends(
                        target_username,
                        followers_list=True,
                        pagination=True,
                        total=1000
                    )
                    
                    if handle_rate_limit(response):
                        retry_count += 1
                        wait_with_backoff(retry_count)
                        continue
                    
                    if response and 'data' in response:
                        followers = response['data']
                        log(f"Found {len(followers)} followers")
                        break  # Success, exit retry loop
                        
                except Exception as e:
                    log(f"Error while fetching followers: {e}", "ERROR")
                    if 'wait' in str(e).lower():
                        retry_count += 1
                        wait_with_backoff(retry_count)
                    else:
                        break  # Break on non-rate-limit errors
            
            if followers:
                # Save basic follower data
                save_to_csv(followers, f'followers_basic_{target_username}')
                
                # Get detailed data with built-in rate limiting
                log("Getting detailed data for public accounts only...")
                detailed_followers = get_detailed_follower_data(insta, followers, max_followers=1000)
                
                if detailed_followers:
                    log(f"Saving detailed data for {len(detailed_followers)} public accounts...")
                    save_to_csv(detailed_followers, f'followers_detailed_{target_username}')
            else:
                log("Failed to fetch followers after max retries", "ERROR")
                
            time.sleep(random.uniform(4, 15))
        else:
            log("Account is private, skipping followers fetch", "WARNING")
                
    except Exception as e:
        log(f"Error occurred: {e}", "ERROR")

if __name__ == "__main__":
    main()