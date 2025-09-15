from decimal import Decimal
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import datetime as dt


# Shared attributes - all optional for maximum flexibility
class PatientBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    aka: Optional[str] = None
    address: Optional[str] = None
    unit_number: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[EmailStr] = None
    language: Optional[str] = None

    # Health info
    # health_card: Optional[str] = None
    # health_card_version: Optional[str] = None
    coverage_type: Optional[str] = None
    disposition: Optional[str] = None
    physician: Optional[str] = None
    # Consent / communication
    patient_consent: Optional[str] = None
    leave_message: bool = False
    voicemail: bool = False
    text: bool = False
    preferred_time: Optional[str] = None
    # Test results
    hiv_date: Optional[dt.date] = None
    hiv_result: Optional[str] = None
    hiv_tester: Optional[str] = None
    hiv_type: Optional[str] = None
    rna_available: Optional[str] = None
    rna_result: Optional[str] = None
    rna_sample_date: Optional[dt.date] = None
    # Referral / registration
    referral_site: Optional[str] = None
    referral_person: Optional[str] = None
    reg_date: Optional[dt.date] = None
    # Notes / misc
    special_attention: Optional[str] = None
    instructions: Optional[str] = None
    selected_template: Optional[str] = None
    summary_template: Optional[str] = None
    test_type: Optional[str] = None
    photo: Optional[str] = None
    finalized_at: Optional[datetime] = None


# Schema for creating a new patient - only require essential fields
class PatientCreate(PatientBase):
    first_name: str
    last_name: str
    dob: dt.date
    health_card: str
    health_card_version: str
    force_create: bool = False
    status: Optional[str] = None


# Schema for updating patient data - inherits all optional fields
class PatientUpdate(PatientBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[dt.date] = None
    health_card: Optional[str] = None
    health_card_version: Optional[str] = None
    status: Optional[str] = None
    force_update: bool = False


class PatientStatus(BaseModel):
    status: str


# Schema for reading patient data (includes DB-generated fields)
class PatientRead(PatientBase):
    id: int
    status: str
    first_name: str
    last_name: str
    dob: dt.date
    health_card: str
    health_card_version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Test Models
class TestBase(BaseModel):
    test_type: Optional[str] = None
    test_date: Optional[dt.date] = None
    # HIV Testing
    hiv_result: Optional[str] = None
    hiv_type: Optional[str] = None
    hiv_tester: Optional[str] = None
    # HCV Testing
    hcv_result: Optional[str] = None
    hcv_tester: Optional[str] = None
    # Bloodwork Testing
    bloodwork_type: Optional[str] = None
    bloodwork_circles: Optional[str] = None
    bloodwork_result: Optional[str] = None
    bloodwork_date_submitted: Optional[dt.date] = None
    bloodwork_tester: Optional[str] = None


class TestCreate(TestBase):
    pass


class TestUpdate(TestBase):
    patient_id: Optional[int] = None


class TestRead(TestBase):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Note Models
class NoteBase(BaseModel):
    note_date: Optional[dt.date] = None
    # template_type: Optional[str] = None


class NoteCreate(NoteBase):
    # patient_id: int  # Required for creation
    note_text: str  # Required for creation
    template_type: str


class NoteUpdate(NoteBase):
    patient_id: Optional[int] = None
    note_text: Optional[str] = None
    template_type: Optional[str] = None


class NoteRead(NoteBase):
    id: int
    patient_id: int
    note_text: str
    template_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Attachment Models
class AttachmentBase(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    is_local: Optional[bool] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    # patient_id: int  # Required for creation
    filename: str  # Required for creation
    document_type: str
    original_url: str


class AttachmentUpdate(AttachmentBase):
    patient_id: Optional[int] = None
    filename: Optional[str] = None
    document_type: Optional[str] = None
    original_url: Optional[str] = None


class AttachmentRead(AttachmentBase):
    id: int
    patient_id: int
    filename: str
    document_type: Optional[str] = None
    original_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Interaction Models
class InteractionBase(BaseModel):
    date: Optional[dt.date] = None
    # description: Optional[str] = None
    referral_id: Optional[str] = None
    amount: Optional[Decimal] = None
    payment_type: Optional[str] = None
    issued: Optional[str] = None


class InteractionCreate(InteractionBase):
    description: str


class InteractionUpdate(InteractionBase):
    patient_id: Optional[int] = None
    description: Optional[str] = None


class InteractionRead(InteractionBase):
    id: int
    description: str
    patient_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Medication Models
class MedicationBase(BaseModel):
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None
    outcome: Optional[str] = None


class MedicationCreate(MedicationBase):
    medication: str  # Required for creation


class MedicationUpdate(MedicationBase):
    patient_id: Optional[int] = None
    medication: Optional[str] = None


class MedicationRead(MedicationBase):
    id: int
    patient_id: int
    medication: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dispensing Models
class DispensingBase(BaseModel):
    rx: Optional[str] = None
    quantity: Optional[int] = None
    lot: Optional[str] = None
    product_type: Optional[str] = None
    expiry_date: Optional[dt.date] = None


class DispensingCreate(DispensingBase):
    # patient_id: int  # Required for creation
    medication: str  # Required for creation


class DispensingUpdate(DispensingBase):
    patient_id: Optional[int] = None
    medication: Optional[str] = None


class DispensingRead(DispensingBase):
    id: int
    patient_id: int
    medication: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Activity Models
class ActivityBase(BaseModel):
    time: Optional[dt.time] = None
    date: Optional[dt.date] = None


class ActivityCreate(ActivityBase):
    # patient_id: int  # Required for creation
    description: str  # Required for creation


class ActivityUpdate(ActivityBase):
    patient_id: Optional[int] = None
    description: Optional[str] = None


class ActivityRead(ActivityBase):
    id: int
    patient_id: int
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientActivity(ActivityBase):
    id: int
    patient_id: int
    first_name: str
    last_name: str
    phone1: Optional[str] = None
    disposition: Optional[str] = None
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
