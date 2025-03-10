import os
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.api.models import ReportRequest, ReportResponse, ReportStatus
from app.services.report_service import generate_report, get_report_status, reports
from app.core.config import REPORTS_DIR

router = APIRouter()

@router.post("/trigger_report", response_model=ReportResponse)
async def trigger_report(background_tasks: BackgroundTasks, request: ReportRequest = None):
    report_id = str(uuid.uuid4())
    reports[report_id] = {"status": "Running", "report_url": None}
    
    background_tasks.add_task(generate_report, report_id)
    
    return {"report_id": report_id}

@router.get("/get_report/{report_id}", response_model=ReportStatus)
async def get_report_by_path(report_id: str):

    report_id = report_id.strip('"')
    
    report_status = get_report_status(report_id)
    if not report_status:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report_status

@router.get("/reports/{report_id}.csv")
async def serve_report(report_id: str):
    report_path = os.path.join(REPORTS_DIR, f"{report_id}.csv")
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(report_path, media_type="text/csv", filename=f"store_report_{report_id}.csv")
