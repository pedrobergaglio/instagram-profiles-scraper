#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database import create_database, init_db
from dotenv import load_dotenv
from database.config import engine, Base, SessionLocal
from database.models import InstagramAccount, Follower, ScrapingSession

def init_db():
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating database if it doesn't exist...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization completed successfully!")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    print("Creating database if it doesn't exist...")
    create_database()
    
    print("Initializing database tables...")
    init_db()
    
    print("Database initialization completed successfully!")

if __name__ == "__main__":
    main() 