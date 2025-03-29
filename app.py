import logging

# Configure logging first, before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)

# Suppress Streamlit warnings
streamlit_loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if name.startswith('streamlit')]
for logger in streamlit_loggers:
    logger.setLevel(logging.ERROR)

import streamlit as st
import pandas as pd
from database.config import SessionLocal, init_db, tables_exist
from database.models import InstagramAccount, Follower, ScrapingSession
from datetime import datetime
from sqlalchemy import func, text
from scraper.manager import ScraperManager
import time
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create logger for this module
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_session_state():
    """Initialize session state variables."""
    if "scraper_manager" not in st.session_state:
        db = get_db()
        st.session_state.scraper_manager = ScraperManager(
            db=db,
            username=os.getenv('INSTAGRAM_USERNAME'),
            password=os.getenv('INSTAGRAM_PASSWORD')
        )
        logger.info(f"Initialized scraper manager with username: {os.getenv('INSTAGRAM_USERNAME')}")
    
    if "active_sessions" not in st.session_state:
        st.session_state.active_sessions = {}

def process_results_background():
    """Background task to process scraping results."""
    logger.info("Starting background processing thread")
    while True:
        if hasattr(st.session_state, "scraper_manager"):
            try:
                st.session_state.scraper_manager.process_results()
            except Exception as e:
                logger.error(f"Error in background processing: {str(e)}")
        time.sleep(1)

def main():
    st.set_page_config(page_title="Instagram Profiles Scraper", layout="wide")
    st.title("Instagram Profiles Scraper")

    # Ensure database is initialized
    if not tables_exist():
        with st.spinner("Initializing database..."):
            init_db()
        st.success("Database initialized successfully!")
        logger.info("Database initialized successfully")

    # Initialize session state
    init_session_state()

    # Start background processing if not already running
    if "background_processor" not in st.session_state:
        background_thread = threading.Thread(
            target=process_results_background,
            daemon=True
        )
        background_thread.start()
        st.session_state.background_processor = background_thread
        logger.info("Started background processing thread")

    # Auto-start scraping for saucotec if not already running
    if "auto_start_done" not in st.session_state:
        logger.info("Auto-starting scraping job for @saucotec")
        session_id = st.session_state.scraper_manager.start_scraping(
            target_username="saucotec",
            max_followers=1000
        )
        if session_id:
            st.session_state.active_sessions[session_id] = {
                "target_username": "saucotec",
                "start_time": datetime.utcnow()
            }
            logger.info(f"Successfully auto-started scraping job for @saucotec (Session #{session_id})")
            st.session_state.auto_start_done = True
        else:
            logger.error("Failed to auto-start scraping job for @saucotec")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Start Scraping", "Accounts", "Followers", "Settings"]
    )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Start Scraping":
        show_scraping_page()
    elif page == "Accounts":
        show_accounts_page()
    elif page == "Followers":
        show_followers_page()
    elif page == "Settings":
        show_settings_page()

def show_dashboard():
    st.header("Dashboard")
    
    db = get_db()
    
    # Get statistics
    total_accounts = db.query(func.count(InstagramAccount.id)).scalar()
    total_followers = db.query(func.count(Follower.id)).scalar()
    active_sessions = db.query(func.count(ScrapingSession.id)).filter(
        ScrapingSession.status == "running"
    ).scalar()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Accounts", total_accounts)
    with col2:
        st.metric("Total Followers", total_followers)
    with col3:
        st.metric("Active Sessions", active_sessions)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Use text() for raw SQL queries
    query = text("""
        SELECT id, target_username, status, created_at, followers_scraped
        FROM scraping_sessions
        ORDER BY created_at DESC
        LIMIT 5
    """)
    result = db.execute(query)
    recent_sessions = result.fetchall()
    
    if recent_sessions:
        session_data = []
        for session in recent_sessions:
            session_data.append({
                "Target Account": session.target_username,
                "Status": session.status,
                "Started": session.created_at,
                "Followers Scraped": session.followers_scraped,
                "Actions": f"Session #{session.id}"
            })
        
        df = pd.DataFrame(session_data)
        st.dataframe(
            df,
            column_config={
                "Actions": st.column_config.Column(
                    "Actions",
                    help="Session actions",
                    width="small"
                )
            }
        )
        
        # Session details
        for session in recent_sessions:
            with st.expander(f"Session #{session.id} Details"):
                status = st.session_state.scraper_manager.get_session_status(session.id)
                st.json(status)
                
                if session.status == "running":
                    if st.button("Stop Session", key=f"stop_{session.id}"):
                        st.session_state.scraper_manager.stop_scraping(session.id)
                        logger.info(f"Stopping session #{session.id}")
                        st.rerun()
    else:
        st.info("No scraping sessions found")

def show_scraping_page():
    st.header("Start New Scraping Job")
    
    with st.form("scraping_form"):
        target_username = st.text_input("Target Instagram Username")
        max_followers = st.number_input("Maximum Followers to Scrape", min_value=1, value=1000)
        use_proxy = st.checkbox("Use Proxy")
        
        if st.form_submit_button("Start Scraping"):
            if target_username:
                logger.info(f"Starting new scraping job for @{target_username}")
                session_id = st.session_state.scraper_manager.start_scraping(
                    target_username=target_username,
                    max_followers=max_followers
                )
                if session_id:
                    st.success(f"Started scraping job for @{target_username} (Session #{session_id})")
                    st.session_state.active_sessions[session_id] = {
                        "target_username": target_username,
                        "start_time": datetime.utcnow()
                    }
                    logger.info(f"Successfully started scraping job for @{target_username} (Session #{session_id})")
                else:
                    error_msg = "Failed to start scraping job"
                    st.error(error_msg)
                    logger.error(f"{error_msg} for @{target_username}")
            else:
                error_msg = "Please enter a target username"
                st.error(error_msg)
                logger.warning(error_msg)

def show_accounts_page():
    st.header("Instagram Accounts")
    
    db = get_db()
    accounts = db.query(InstagramAccount).all()
    
    if accounts:
        account_data = []
        for account in accounts:
            account_data.append({
                "Username": account.username,
                "Followers": account.follower_count,
                "Following": account.following_count,
                "Posts": account.post_count,
                "Last Updated": account.updated_at
            })
        st.dataframe(pd.DataFrame(account_data))
        logger.debug(f"Displaying {len(account_data)} accounts")
    else:
        st.info("No accounts found in the database")
        logger.debug("No accounts found in database")

def show_followers_page():
    st.header("Followers Data")
    
    db = get_db()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search by username")
    with col2:
        min_followers = st.number_input("Minimum followers", value=0)
    with col3:
        is_verified = st.selectbox(
            "Verification Status",
            options=["All", "Verified Only", "Non-verified Only"]
        )
    
    # Query with filters
    query = db.query(Follower)
    if search:
        query = query.filter(Follower.username.like(f"%{search}%"))
    if min_followers > 0:
        query = query.filter(Follower.follower_count >= min_followers)
    if is_verified != "All":
        query = query.filter(Follower.is_verified == (is_verified == "Verified Only"))
    
    followers = query.limit(1000).all()
    
    if followers:
        follower_data = []
        for follower in followers:
            follower_data.append({
                "Username": follower.username,
                "Full Name": follower.full_name,
                "Followers": follower.follower_count,
                "Following": follower.following_count,
                "Posts": follower.post_count,
                "Private": follower.is_private,
                "Verified": follower.is_verified
            })
        
        df = pd.DataFrame(follower_data)
        
        # Add download button
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Data",
            csv,
            "instagram_followers.csv",
            "text/csv",
            key="download-csv"
        )
        
        st.dataframe(df)
        logger.debug(f"Displaying {len(follower_data)} followers")
    else:
        st.info("No followers found matching the criteria")
        logger.debug("No followers found matching criteria")

def show_settings_page():
    st.header("Settings")
    
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Scraping Settings")
            batch_size = st.number_input("Batch Size", min_value=1, value=50)
            delay = st.number_input("Delay between requests (seconds)", min_value=1, value=2)
            max_retries = st.number_input("Maximum retries per request", min_value=1, value=3)
        
        with col2:
            st.subheader("Proxy Settings")
            proxy_enabled = st.checkbox("Enable Proxy")
            proxy_url = st.text_input("Proxy URL")
            proxy_rotation = st.checkbox("Enable Proxy Rotation")
        
        if st.form_submit_button("Save Settings"):
            # Update scraper manager settings
            st.session_state.scraper_manager = ScraperManager(
                db=get_db(),
                batch_size=batch_size,
                delay=delay,
                username=os.getenv('INSTAGRAM_USERNAME'),
                password=os.getenv('INSTAGRAM_PASSWORD')
            )
            st.success("Settings saved successfully")
            logger.info("Updated scraper settings")

    # Danger Zone
    st.subheader("Danger Zone")
    if st.button("Stop All Scraping Jobs", type="secondary"):
        st.session_state.scraper_manager.stop_all()
        st.warning("All scraping jobs have been stopped")
        logger.warning("All scraping jobs stopped by user")

if __name__ == "__main__":
    main()