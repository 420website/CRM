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


class GuestValidateRequest(BaseModel):
    passcode: str
    guest_id: str


class SessionConfig(BaseModel):
    session_name: str
    session_key: str
    host_id: int
    is_locked: bool
    host_last_seen_at: str  # ISO timestamp

    def encode(self):
        return {
            "session_name": self.session_name,
            "session_key": self.session_key,
            "host_id": str(self.host_id),
            "is_locked": str(self.is_locked),
            "host_last_seen_at": self.host_last_seen_at,
        }

    @classmethod
    def decode(cls, data: dict) -> "SessionConfig":
        """Decode Redis hash (all strings) into typed SessionConfig."""
        return cls(
            session_name=data["session_name"],
            session_key=data["session_key"],
            host_id=int(data["host_id"]),
            is_locked=data["is_locked"].lower() == "true",
            host_last_seen_at=data["host_last_seen_at"],
        )

    class Config:
        from_attributes = True
