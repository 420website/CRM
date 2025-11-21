from decimal import Decimal
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import datetime as dt


class IdentityCheck(BaseModel):
    first_name: str
    last_name: str
    dob: dt.date
    id: Optional[int] = None

    @field_validator("first_name", "last_name")
    def normalize_name(cls, v):
        return v.strip().title() if v else v


class IdentityUser(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class HealthcardCheck(BaseModel):
    health_card: str
    id: Optional[int] = None


class HealthcardUser(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


# Shared attributes - all optional for maximum flexibility
class PatientBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    health_card: Optional[str] = None
    health_card_version: Optional[str] = None
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
    finalized_at: Optional[datetime] = None


# Schema for creating a new patient - only require essential fields
class PatientCreate(PatientBase):
    first_name: str
    last_name: str
    dob: dt.date
    force_create: bool = False
    limited: bool = True
    status: Optional[str] = None

    @field_validator("first_name", "last_name", "aka")
    def normalize_name(cls, v):
        return v.strip().title() if v else v


# Schema for updating patient data - inherits all optional fields
class PatientUpdate(PatientBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[dt.date] = None
    force_update: bool = False
    limited: bool = True
    status: Optional[str] = None

    @field_validator("first_name", "last_name", "aka")
    def normalize_name(cls, v):
        return v.strip().title() if v else v


class PatientStatus(BaseModel):
    status: str


# Schema for reading patient data (includes DB-generated fields)
class PatientRead(PatientBase):
    id: int
    status: str
    first_name: str
    last_name: str
    dob: dt.date
    limited: bool
    health_card: Optional[str] = None
    health_card_version: Optional[str] = None
    file_id: Optional[str] = None
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
    # completed: Optional[bool] = False


class ActivityCreate(ActivityBase):
    name: str
    description: str


class ActivityUpdate(ActivityBase):
    patient_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class ActivityRead(ActivityBase):
    id: int
    patient_id: int
    description: str
    name: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientActivity(ActivityBase):
    id: int
    patient_id: int
    first_name: str
    last_name: str
    status: str
    submitted_date: datetime
    finalized_at: Optional[datetime] = None
    reg_date: Optional[dt.date] = None
    file_id: Optional[str] = None
    phone1: Optional[str] = None
    disposition: Optional[str] = None
    referral_site: Optional[str] = None
    name: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
