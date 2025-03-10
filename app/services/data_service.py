import os
import pandas as pd

from app.core.config import DATA_DIR, logger
from app.db.database import create_db_connection, create_tables


def validate_csv(file_path, required_columns):
    try:
        df = pd.read_csv(file_path)
        if not all(column in df.columns for column in required_columns):
            raise ValueError(f"Missing required columns in {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error validating CSV file {file_path}: {str(e)}")
        raise
def ingest_data():
    try:
        engine = create_db_connection()
        create_tables(engine)
        
        store_status_path = os.path.join(DATA_DIR, 'store_status.csv')
        menu_hours_path = os.path.join(DATA_DIR, 'menu_hours.csv')
        store_timezone_path = os.path.join(DATA_DIR, 'store_timezone.csv')
        
        if not os.path.exists(store_status_path):
            raise FileNotFoundError(f"store_status.csv not found in {DATA_DIR}")
        if not os.path.exists(menu_hours_path):
            raise FileNotFoundError(f"menu_hours.csv not found in {DATA_DIR}")
        if not os.path.exists(store_timezone_path):
            raise FileNotFoundError(f"store_timezone.csv not found in {DATA_DIR}")

        store_status_df = validate_csv(store_status_path, ['store_id', 'timestamp_utc', 'status'])
        menu_hours_df = validate_csv(menu_hours_path, ['store_id', 'day', 'start_time_local', 'end_time_local'])
        timezone_df = validate_csv(store_timezone_path, ['store_id', 'timezone_str'])
        
        store_status_df.to_sql('store_status', engine, if_exists='replace', index=False)
        menu_hours_df.to_sql('menu_hours', engine, if_exists='replace', index=False)
        timezone_df.to_sql('store_timezone', engine, if_exists='replace', index=False)
        
        logger.info("Data ingestion completed successfully")
        return True
    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        return False