import os
import pandas as pd
import pytz
from datetime import datetime, timedelta
import numpy as np

from app.db.database import create_db_connection, check_data_exists
from app.services.data_service import ingest_data
from app.core.config import REPORTS_DIR, logger
from app.utils.helpers import convert_to_utc, convert_to_local, is_within_business_hours, calculate_uptime_downtime


reports = {}

def get_report_status(report_id: str):
    if report_id not in reports:
        return None
    return reports[report_id]


def generate_report(report_id: str):
    try:
        if not check_data_exists():
            logger.warning("No data found in database tables, attempting to ingest data...")
            if not ingest_data():
                logger.error("Data ingestion failed")
                reports[report_id] = {"status": "Failed", "report_url": None}
                return
        
        engine = create_db_connection()
        
        store_status = pd.read_sql("SELECT * FROM store_status", engine)
        menu_hours = pd.read_sql("SELECT * FROM menu_hours", engine)
        timezones = pd.read_sql("SELECT * FROM store_timezone", engine)
        
        store_status['timestamp_utc'] = pd.to_datetime(store_status['timestamp_utc'])
        
        current_time = store_status['timestamp_utc'].max()
        logger.info(f"Using {current_time} as the current time reference")
        
        result = []
        
        for store_id in timezones['store_id'].unique():
            logger.info(f"Processing store {store_id}")
            
            timezone_str = timezones[timezones['store_id'] == store_id]['timezone_str'].iloc[0]
            store_hours = menu_hours[menu_hours['store_id'] == store_id]
            store_observations = store_status[store_status['store_id'] == store_id]
            
            uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(
                store_observations, store_hours, timezone_str, period_hours=1)
            uptime_last_day, downtime_last_day = calculate_uptime_downtime(
                store_observations, store_hours, timezone_str, period_hours=24)
            uptime_last_week, downtime_last_week = calculate_uptime_downtime(
                store_observations, store_hours, timezone_str, period_hours=168)
            
            result.append({
                'store_id': store_id,
                'uptime_last_hour': uptime_last_hour,
                'uptime_last_day': uptime_last_day,
                'uptime_last_week': uptime_last_week,
                'downtime_last_hour': downtime_last_hour,
                'downtime_last_day': downtime_last_day,
                'downtime_last_week': downtime_last_week
            })
        
        report_df = pd.DataFrame(result)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        report_path = os.path.join(REPORTS_DIR, f"{report_id}.csv")
        report_df.to_csv(report_path, index=False)
        
        reports[report_id] = {"status": "Complete", "report_url": f"/reports/{report_id}.csv"}
        logger.info(f"Report {report_id} generated successfully")
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        reports[report_id] = {"status": "Failed", "report_url": None}