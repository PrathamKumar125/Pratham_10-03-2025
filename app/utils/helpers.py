import pytz
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.core.config import logger

def convert_to_utc(local_time, timezone_str):
    try:
        local_tz = pytz.timezone(timezone_str)
        utc_tz = pytz.UTC
        local_dt = local_tz.localize(local_time)
        utc_dt = local_dt.astimezone(utc_tz)

        return utc_dt
    except Exception as e:
        raise Exception(f"Error converting to UTC: {str(e)}")

def convert_to_local(utc_time, timezone_str):
    local_tz = pytz.timezone(timezone_str)
    return utc_time.astimezone(local_tz)

def convert_to_local(utc_time, timezone_str):
    try:
        local_tz = pytz.timezone(timezone_str)
        if utc_time.tzinfo is None:
            utc_time = pytz.UTC.localize(utc_time)
        
        local_dt = utc_time.astimezone(local_tz)
        return local_dt
    except Exception as e:
        raise Exception(f"Error converting to local time: {str(e)}")

def is_within_business_hours(local_time, business_hours):
    if business_hours.empty:
        return True  # 24/7
    for _, row in business_hours.iterrows():
        start_time = datetime.strptime(row["start_time_local"], "%H:%M:%S").time()
        end_time = datetime.strptime(row["end_time_local"], "%H:%M:%S").time()

        business_start = local_time.replace(
            hour=start_time.hour, 
            minute=start_time.minute, 
            second=0, 
            microsecond=0
        )
        business_end = local_time.replace(
            hour=end_time.hour,
            minute=end_time.minute,
            second=0,
            microsecond=0
        )

        if business_end < business_start:
            business_end += timedelta(days=1)

        if business_start <= local_time <= business_end:
            return True

    return False

def calculate_uptime_downtime(status_data, business_hours, timezone_str, period_hours=1):
    
    if status_data.empty:
        logger.warning("No status data available for store")
        return 0, 0
        
    if not timezone_str:
        logger.warning("No timezone provided, defaulting to UTC")
        timezone_str = 'UTC'
    
    max_timestamp = status_data['timestamp_utc'].max()
    period_start = max_timestamp - timedelta(hours=period_hours)
    period_data = status_data[status_data['timestamp_utc'] >= period_start].copy()
    
    if period_data.empty:
        logger.warning(f"No data available for the last {period_hours} hours")
        return 0, 0
    
    local_tz = pytz.timezone(timezone_str)
    period_data['timestamp_local'] = period_data['timestamp_utc'].apply(
        lambda x: x.astimezone(local_tz) if x.tzinfo else pytz.UTC.localize(x).astimezone(local_tz))
    
    period_data.sort_values('timestamp_utc', inplace=True)
    
    period_data['next_timestamp'] = period_data['timestamp_utc'].shift(-1)
    period_data['time_diff'] = (period_data['next_timestamp'] - period_data['timestamp_utc']).dt.total_seconds() / 60
    
    period_data = period_data.dropna(subset=['time_diff'])
    
    uptime_minutes = 0
    downtime_minutes = 0
    
    for _, row in period_data.iterrows():
        start_time = row['timestamp_local']
        end_time = start_time + timedelta(minutes=row['time_diff'])
        
        current = start_time
        while current < end_time:
            is_business_hour = is_within_business_hours(current, business_hours)
            
            if is_business_hour:
                if row['status'] == 'active':
                    uptime_minutes += 1
                else:
                    downtime_minutes += 1
            
            current += timedelta(minutes=1)
    
    if not period_data.empty:
        last_status = period_data.iloc[-1]['status']
        last_timestamp_local = period_data.iloc[-1]['timestamp_local']
        minutes_to_current = int((max_timestamp - period_data.iloc[-1]['timestamp_utc']).total_seconds() / 60)
        
        for i in range(minutes_to_current):
            check_time = last_timestamp_local + timedelta(minutes=i)
            is_business_hour = is_within_business_hours(check_time, business_hours)
            
            if is_business_hour:
                if last_status == 'active':
                    uptime_minutes += 1
                else:
                    downtime_minutes += 1
    
    return uptime_minutes, downtime_minutes