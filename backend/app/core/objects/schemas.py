from pydantic import BaseModel
from datetime import datetime


class AttachmentId(BaseModel):
    attachment_id: int


class AttachmentCreate(BaseModel):
    file_name: str
    file_key: str
    file_size: int
    mime_type: str
    document_type: str


class AttachmentRead(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_key: str
    file_size: int
    mime_type: str
    document_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PhotoCreate(BaseModel):
    photo_name: str
    photo_key: str


class PhotoRead(BaseModel):
    id: int
    patient_id: int
    photo_name: str
    photo_key: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
