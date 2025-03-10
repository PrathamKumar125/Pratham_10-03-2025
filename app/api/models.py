from pydantic import BaseModel

class ReportRequest(BaseModel):
    class Config:
        extra = "ignore"  

class ReportResponse(BaseModel):
    report_id: str

class ReportStatus(BaseModel):
    status: str
    report_url: str = None
