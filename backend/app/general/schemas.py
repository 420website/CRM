from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Notes
class NotesTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    content: str
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotesTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


class NotesTemplateDelete(BaseModel):
    name: str


# Clinical
class ClinicalTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    content: str
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClinicalTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# Dispositions
class Disposition(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DispositionUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# Document Types
class DocumentType(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentTypeUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# Referral Sites
class ReferralSite(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferralSiteUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# Medication
class Medication(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# Medication Outcome
class MedicationOutcome(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MedicationOutcomeUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None


# General Fields
class General(BaseModel):
    id: Optional[int] = None
    name: str
    is_frequent: bool
    is_default: bool
    type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GeneralUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: Optional[datetime] = None
