# pyright: reportAssignmentType=none
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import datetime as dt


# Shared attributes - all optional for maximum flexibility
class RawAnalytics(BaseModel):
    # Registration data
    patientid: int
    dob: dt.date
    gender: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    province: Optional[str] = ""
    postalcode: Optional[str] = ""
    phone: Optional[str] = ""
    healthcard: Optional[str] = ""
    disposition: Optional[str] = ""
    regdate: dt.date
    referralsite: Optional[str] = ""
    # Interactions data
    interactiontype: Optional[str] = ""
    amount: Optional[int] = 0

    class Config:
        from_attributes = True


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
    # chart_html: Optional[str] = None
    # chart_image_url: Optional[str] = None


# Excel Upload Models
class ExcelUploadResponse(BaseModel):
    message: str
    records_count: int
    preview: List[dict]
    upload_id: str


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


@dataclass
class AnalyticsStats:
    """Container for all analytics statistics"""

    total_records: int = 0
    dispositions: Dict[str, int] = None
    dispositions_2024: Dict[str, int] = None
    dispositions_2025: Dict[str, int] = None
    genders: Dict[str, int] = None
    genders_2024: Dict[str, int] = None
    genders_2025: Dict[str, int] = None
    phone_stats: Dict[str, int] = None
    health_card_stats: Dict[str, int] = None
    address_stats: Dict[str, int] = None
    rewards_stats: Dict[str, Any] = None
    age_stats: Dict[str, Any] = None
    monthly_counts: Dict[str, int] = None
    yearly_data: Dict[str, int] = None

    def __post_init__(self):
        if self.dispositions is None:
            self.dispositions = {}
        if self.dispositions_2024 is None:
            self.dispositions_2024 = {}
        if self.dispositions_2025 is None:
            self.dispositions_2025 = {}
        if self.genders is None:
            self.genders = {}
        if self.genders_2024 is None:
            self.genders_2024 = {}
        if self.genders_2025 is None:
            self.genders_2025 = {}
        if self.phone_stats is None:
            self.phone_stats = {
                "total_records": 0,
                "no_phone_count": 0,
                "valid_phone_count": 0,
            }
        if self.health_card_stats is None:
            self.health_card_stats = {
                "total_records": 0,
                "no_hc_count": 0,
                "invalid_hc_count": 0,
                "valid_hc_count": 0,
            }
        if self.address_stats is None:
            self.address_stats = {
                "total_records": 0,
                "no_address_count": 0,
                "valid_address_count": 0,
            }
        if self.rewards_stats is None:
            self.rewards_stats = {
                "total_amount": 0,
                "total_records_with_amount": 0,
                "monthly_totals_2024": {},
                "monthly_totals_2025": {},
                "yearly_totals": {"2024": 0, "2025": 0},
            }
        if self.age_stats is None:
            self.age_stats = {
                "total_records_with_age": 0,
                "age_ranges": {
                    "0-19": 0,
                    "20-29": 0,
                    "30-39": 0,
                    "40-49": 0,
                    "50-59": 0,
                    "60-69": 0,
                    "70-79": 0,
                    "80-89": 0,
                    "90+": 0,
                },
            }
        if self.monthly_counts is None:
            self.monthly_counts = {}
        if self.yearly_data is None:
            self.yearly_data = {}
