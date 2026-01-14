# Request/Response models
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class ClaudeChatRequest(BaseModel):
    legacy_data: bool
    message: str
    datetime: str
    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4())
    )

class ClaudeChatResponse(BaseModel):
    response: str
    session_id: str


# Excel Upload Models
class ExcelUploadResponse(BaseModel):
    message: str
    records_count: int
    preview: List[dict]
    upload_id: str

class DataSummaryResponse(BaseModel):
    total_records: int
    date_range: dict
    top_dispositions: List[dict]
    upload_info: dict

# Legacy Data
class LegacyData(BaseModel):
    user_id: int
    upload_id: str
    filename: str
    upload_date: datetime
    records_count: int
    columns: list
    data: list

    class Config:
        from_attributes = True

