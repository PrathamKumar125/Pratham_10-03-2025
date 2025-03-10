# Store Monitoring System

A system to monitor restaurant uptime and downtime during business hours, calculate metrics, and generate reports.

## Overview

This application provides an API for restaurant owners to monitor their store's online/offline status. It calculates uptime and downtime metrics for each store considering their specific business hours and timezones.

## Features

- Ingests data from CSV files into SQLite database
- Handles different timezones for each store
- Considers store-specific business hours
- Calculates uptime and downtime for different time periods:
  - Last hour (in minutes)
  - Last day (in hours)
  - Last week (in hours)
- Async report generation via background tasks
- API endpoints for triggering and retrieving reports

## Database Schema

The system uses three tables:
- `store_status`: Contains polling data for each store
- `business_hours`: Contains business hours for each store
- `store_timezones`: Contains timezone information for each store

## API Endpoints

1. **POST /trigger_report**
   - Starts a background task to generate a store monitoring report
   - Returns a unique report ID for tracking
   - Note: This endpoint accepts an empty JSON body `{}`

2. **GET /get_report**
   - Query parameter: `report_id` - The unique ID returned from the trigger_report endpoint
   - Example: `/get_report?report_id=b7bbf2d5-e481-42bb-824c-0f39797d0e6d`
   - Returns the report status ("Running", "Complete", etc.)
   - Returns the report URL when the report is complete

   Alternatively, you can use the path parameter format:
   - **GET /get_report/{report_id}**
   - Example: `/get_report/b7bbf2d5-e481-42bb-824c-0f39797d0e6d`

3. **GET /reports/{report_id}.csv**
   - Serves the generated CSV report file

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Import data:
   ```
   python ingest_data.py
   ```

3. Run the FastAPI application:
   ```
   uvicorn app:app --reload
   ```

4. Access the API at http://localhost:8000

## Example Usage

1. Trigger a report:
   ```
   curl -X POST http://localhost:8000/trigger_report -H "Content-Type: application/json" -d "{}"
   ```

2. Check the report status (using query parameter):
   ```
   curl "http://localhost:8000/get_report?report_id=b7bbf2d5-e481-42bb-824c-0f39797d0e6d"
   ```

   Or using path parameter:
   ```
   curl http://localhost:8000/get_report/b7bbf2d5-e481-42bb-824c-0f39797d0e6d
   ```

3. Download the report (when status is "Complete"):
   ```
   curl -o report.csv http://localhost:8000/reports/b7bbf2d5-e481-42bb-824c-0f39797d0e6d.csv
   ```

## Testing

Run the included test script:
```
python test_api.py
```

This will test the trigger_report and get_report endpoints and verify the workflow.

## Future Improvements

Here are some ideas for improving the solution:

1. **User Authentication**: Add user authentication and authorization to secure the API endpoints.
2. **Historical Data Analysis**: Implement features to analyze historical data trends and provide insights over longer periods.
3. **Notification System**: Develop a notification system to alert store owners of significant status changes or downtime events.
4. **UI Dashboard**: Create a user-friendly web dashboard for visualizing store status, uptime, and downtime metrics.
5. **Real-time Data Sync**: Use Celery to schedule and manage real-time data synchronization tasks every 2 hours to ensure the database is up-to-date.
