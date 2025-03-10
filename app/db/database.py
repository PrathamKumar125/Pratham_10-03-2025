import pandas as pd
from sqlalchemy import create_engine, text

from app.core.config import DATABASE_URL, logger


def create_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise


def check_data_exists():
    try:
        engine = create_db_connection()
        with engine.connect() as conn:
            store_status_count = conn.execute(text("SELECT COUNT(*) FROM store_status")).scalar()
            menu_hours_count = conn.execute(text("SELECT COUNT(*) FROM menu_hours")).scalar()
            timezone_count = conn.execute(text("SELECT COUNT(*) FROM store_timezone")).scalar()
            
        if store_status_count == 0:
            logger.debug("No data found in store_status table.")
            return False
        if menu_hours_count == 0:
            logger.debug("No data found in menu_hours table.")
            return False
        if timezone_count == 0:
            logger.debug("No data found in timezone table.")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking data existence: {str(e)}")
        return False




def create_tables(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS store_status (
                    store_id TEXT,
                    timestamp_utc TEXT,
                    status TEXT,
                    PRIMARY KEY (store_id, timestamp_utc)
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS menu_hours (
                    store_id TEXT,
                    day INTEGER,
                    start_time_local TEXT,
                    end_time_local TEXT,
                    PRIMARY KEY (store_id, day, start_time_local)
                )
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS store_timezone (
                    store_id TEXT PRIMARY KEY,
                    timezone_str TEXT
                )
            '''))
            conn.commit()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def fetch_store_data(engine, store_id):
    """Fetch all data for a specific store."""
    try:
        with engine.connect() as conn:
            store_status = pd.read_sql(
                f"SELECT * FROM store_status WHERE store_id = '{store_id}'", conn
            )
            menu_hours = pd.read_sql(
                f"SELECT * FROM menu_hours WHERE store_id = '{store_id}'", conn
            )
            timezone = pd.read_sql(
                f"SELECT * FROM store_timezone WHERE store_id = '{store_id}'", conn
            )
            return store_status, menu_hours, timezone
    except Exception as e:
        logger.error(f"Error fetching store data: {str(e)}")
        raise