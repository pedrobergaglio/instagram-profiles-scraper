from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .models import Base
import os

# Database configuration
DB_USER = os.getenv('MYSQL_DB_USER', 'appsheet')
DB_PASSWORD = os.getenv('MYSQL_DB_PASSWORD', 'Myeest822')
DB_HOST = os.getenv('MYSQL_DB_HOST', '149.50.134.100')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('MYSQL_SYSTEM_DB_NAME', 'profiles_scraped')

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def tables_exist():
    """Check if all required tables exist."""
    inspector = inspect(engine)
    required_tables = {'instagram_accounts', 'scraping_sessions', 'followers'}
    existing_tables = set(inspector.get_table_names())
    return required_tables.issubset(existing_tables)

def init_db():
    """Initialize the database, creating all tables."""
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session."""
    if not tables_exist():
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database():
    """Create the database if it doesn't exist."""
    # Create engine without database name
    base_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    temp_engine = create_engine(base_url)
    
    # Create database if it doesn't exist
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conn.execute(text(f"USE {DB_NAME}"))
        conn.commit()
    
    temp_engine.dispose()
    
    # Initialize tables if they don't exist
    if not tables_exist():
        init_db()