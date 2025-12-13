from datetime import datetime
from pydantic import BaseModel
from app.config import settings


class Session(BaseModel):
    tpc: str  # Unique session ID (e.g., "patient_123")
    role_type: str  # 1=host, 0=participant
    iat: int
    exp: int
    version: int = 1  # Always 1
    app_key: str = settings.sdk_key  #  Zoom app identifier


class JoinResponse(BaseModel):
    access_token: str
    sessionPasscode: str
    sessionName: str
    expires_at: datetime
    token_type: str = "bearer"
