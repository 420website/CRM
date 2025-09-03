# app/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class DataSummaryResponse(BaseModel):
    total_records: int
    date_range: dict
    top_dispositions: List[dict]
    upload_info: dict


# Claude AI Chat Models
class ClaudeChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4())
    )
    generate_chart: Optional[bool] = Field(
        default=False, description="Request chart generation"
    )


class ClaudeChatResponse(BaseModel):
    response: str
    session_id: str
    chart_html: Optional[str] = None
    chart_image_url: Optional[str] = None


# Excel Upload Models
class ExcelUploadResponse(BaseModel):
    message: str
    records_count: int
    preview: List[dict]
    upload_id: str
