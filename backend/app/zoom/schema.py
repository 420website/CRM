from datetime import datetime
import json
from typing import List
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


class SyncParticipantsRequest(BaseModel):
    session_key: str
    zoom_participants: List[str]


class SessionConfig(BaseModel):
    # id: int
    patient_id: int
    session_name: str
    session_key: str
    host_id: int
    is_locked: bool
    locked_at: datetime | None
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime | None

    def encode(self):
        """Encode session data for Redis storage (as hash)"""
        data = {
            "patient_id": str(self.patient_id),
            "session_name": self.session_name,
            "session_key": self.session_key,
            "host_id": str(self.host_id),
            "is_locked": str(self.is_locked),
            "is_deleted": str(self.is_deleted),
        }

        # Only include datetime fields if they're not None
        if self.locked_at:
            data["locked_at"] = self.locked_at.isoformat()
        if self.deleted_at:
            data["deleted_at"] = self.deleted_at.isoformat()
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()

        return data

    @classmethod
    def decode(cls, data):
        """Decode session data from Redis hash"""
        return cls(
            patient_id=int(
                data[b"patient_id"]
                if isinstance(data[b"patient_id"], bytes)
                else data["patient_id"]
            ),
            session_name=(
                data[b"session_name"].decode()
                if isinstance(data.get(b"session_name"), bytes)
                else data["session_name"]
            ),
            session_key=(
                data[b"session_key"].decode()
                if isinstance(data.get(b"session_key"), bytes)
                else data["session_key"]
            ),
            host_id=int(
                data[b"host_id"]
                if isinstance(data[b"host_id"], bytes)
                else data["host_id"]
            ),
            is_locked=(
                data.get(b"is_locked", b"False").decode() == "True"
                if isinstance(data.get(b"is_locked"), bytes)
                else data.get("is_locked") == "True"
            ),
            locked_at=(
                datetime.fromisoformat(data[b"locked_at"].decode())
                if data.get(b"locked_at")
                else None
            ),
            is_deleted=(
                data.get(b"is_deleted", b"False").decode() == "True"
                if isinstance(data.get(b"is_deleted"), bytes)
                else data.get("is_deleted") == "True"
            ),
            deleted_at=(
                datetime.fromisoformat(data[b"deleted_at"].decode())
                if data.get(b"deleted_at")
                else None
            ),
            created_at=(
                datetime.fromisoformat(data[b"created_at"].decode())
                if data.get(b"created_at")
                else None
            ),
        )

    class Config:
        from_attributes = True
