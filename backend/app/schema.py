from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    validator,
)
from typing import List, Optional
import uuid
from datetime import datetime, date
import pytz
import re


# Define Models
class UserRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    health_card_number: Optional[str] = Field(
        None, min_length=10, max_length=12
    )
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    consent_given: bool = Field(..., description="User must give consent")
    consent_timestamp: datetime = Field(default_factory=datetime.utcnow)
    registration_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(
        default="pending", description="pending, confirmed, completed"
    )

    @validator("health_card_number")
    def validate_health_card(cls, v):
        if v is not None:  # Only validate if provided
            # Remove any spaces or dashes
            v = re.sub(r"[\s-]", "", v)
            if not v.isdigit():
                raise ValueError("Health card number must contain only digits")
            if len(v) < 10 or len(v) > 12:
                raise ValueError(
                    "Health card number must be between 10-12 digits"
                )
        return v

    @validator("phone_number")
    def validate_phone(cls, v):
        # Remove any non-digit characters
        v = re.sub(r"[^\d]", "", v)
        if len(v) != 10:
            raise ValueError("Phone number must be 10 digits")
        return v

    @validator("consent_given")
    def validate_consent(cls, v):
        if not v:
            raise ValueError(
                "Consent must be given to proceed with registration"
            )
        return v

    @validator("email")
    def validate_contact_info(cls, v, values):
        # Require either phone or email
        phone = values.get("phone_number")
        if not phone and not v:
            raise ValueError(
                "Either phone number or email address is required"
            )
        return v


class UserRegistrationCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    health_card_number: Optional[str] = Field(
        None, min_length=10, max_length=12
    )
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    consent_given: bool = Field(..., description="User must give consent")

    @validator("health_card_number")
    def validate_health_card(cls, v):
        if v is not None:  # Only validate if provided
            # Remove any spaces or dashes
            v = re.sub(r"[\s-]", "", v)
            if not v.isdigit():
                raise ValueError("Health card number must contain only digits")
            if len(v) < 10 or len(v) > 12:
                raise ValueError(
                    "Health card number must be between 10-12 digits"
                )
        return v

    @validator("email")
    def validate_contact_info(cls, v, values):
        # Require either phone or email
        phone = values.get("phone_number")
        if not phone and not v:
            raise ValueError(
                "Either phone number or email address is required"
            )
        return v


class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=10, max_length=1000)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )
    status: str = Field(default="new")


class ContactMessageCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=10, max_length=1000)


class AdminRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    dob: Optional[date] = None
    patientConsent: str = Field(
        ..., description="Consent type: verbal or written"
    )
    gender: Optional[str] = None
    province: Optional[str] = Field(default="Ontario")
    disposition: Optional[str] = None
    aka: Optional[str] = None
    age: Optional[str] = None
    regDate: Optional[date] = Field(default_factory=date.today)
    healthCard: Optional[str] = None
    healthCardVersion: Optional[str] = None  # Health card version code
    referralSite: Optional[str] = None
    address: Optional[str] = None
    unitNumber: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    ext1: Optional[str] = None
    ext2: Optional[str] = None
    leaveMessage: bool = Field(default=False)
    voicemail: bool = Field(default=False)
    text: bool = Field(default=False)
    preferredTime: Optional[str] = None
    email: Optional[EmailStr] = None
    language: str = Field(default="English")
    specialAttention: Optional[str] = None
    instructions: Optional[str] = None
    photo: Optional[str] = None  # Base64 encoded photo
    summaryTemplate: Optional[str] = None  # Clinical summary template
    selectedTemplate: Optional[str] = Field(
        default="Select"
    )  # Selected template name
    physician: Optional[str] = Field(
        default="Dr. David Fletcher"
    )  # Physician field
    rnaAvailable: Optional[str] = Field(default="No")  # RNA available field
    rnaSampleDate: Optional[str] = None  # RNA sample date field
    rnaResult: Optional[str] = Field(default="Positive")  # RNA result field
    coverageType: Optional[str] = Field(
        default="Select"
    )  # Coverage type field
    referralPerson: Optional[str] = None  # Person who referred the patient
    testType: Optional[str] = Field(default="Tests")  # Test type field
    # HIV Test Fields
    hivDate: Optional[str] = None  # HIV test date
    hivResult: Optional[str] = None  # HIV test result (negative/positive)
    hivType: Optional[str] = None  # HIV type (Type 1/Type 2)
    hivTester: Optional[str] = Field(default="CM")  # HIV tester initials
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )
    status: str = Field(default="pending_review")
    attachments: Optional[List[dict]] = Field(
        default_factory=list
    )  # Document attachments


class AdminRegistrationCreate(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    dob: Optional[date] = None
    patientConsent: str = Field(
        ..., description="Consent type: verbal or written"
    )
    gender: Optional[str] = None
    province: Optional[str] = Field(default="Ontario")
    disposition: Optional[str] = None
    aka: Optional[str] = None
    age: Optional[str] = None
    regDate: Optional[date] = Field(default_factory=date.today)
    healthCard: Optional[str] = None
    healthCardVersion: Optional[str] = None  # Health card version code
    referralSite: Optional[str] = None
    address: Optional[str] = None
    unitNumber: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    ext1: Optional[str] = None
    ext2: Optional[str] = None
    leaveMessage: bool = Field(default=False)
    voicemail: bool = Field(default=False)
    text: bool = Field(default=False)
    preferredTime: Optional[str] = None
    email: Optional[EmailStr] = None
    language: str = Field(default="English")
    specialAttention: Optional[str] = None
    instructions: Optional[str] = None
    photo: Optional[str] = None  # Base64 encoded photo
    summaryTemplate: Optional[str] = None  # Clinical summary template
    selectedTemplate: Optional[str] = Field(
        default="Select"
    )  # Selected template name
    physician: Optional[str] = Field(
        default="Dr. David Fletcher"
    )  # Physician field
    rnaAvailable: Optional[str] = Field(default="No")  # RNA available field
    rnaSampleDate: Optional[str] = None  # RNA sample date field
    rnaResult: Optional[str] = Field(default="Positive")  # RNA result field
    coverageType: Optional[str] = Field(
        default="Select"
    )  # Coverage type field
    testType: Optional[str] = Field(default="Tests")  # Test type field
    # HIV Test Fields
    hivDate: Optional[str] = None  # HIV test date
    hivResult: Optional[str] = None  # HIV test result (negative/positive)
    hivType: Optional[str] = None  # HIV type (Type 1/Type 2)
    hivTester: Optional[str] = Field(default="CM")  # HIV tester initials


# 2FA Models
class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str = "admin"  # Single admin for now, expandable
    pin_hash: str  # Existing PIN (bcrypt hashed)

    # 2FA Fields
    two_fa_enabled: bool = False
    totp_secret: Optional[str] = None  # Encrypted TOTP secret
    backup_codes: List[str] = Field(
        default_factory=list
    )  # Hashed backup codes

    # Security Tracking
    last_totp_used: Optional[datetime] = None  # Prevent replay attacks
    failed_2fa_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None

    # Session Management
    current_session_token: Optional[str] = None
    session_expires: Optional[datetime] = None


class TwoFactorSetupResponse(BaseModel):
    qr_code_data: str  # Base64 encoded QR code image
    backup_codes: List[str]  # Display-only, not stored in plain text
    totp_secret: str  # For manual entry if QR doesn't work
    setup_complete: bool = False


class TwoFactorVerifyRequest(BaseModel):
    totp_code: Optional[str] = None
    backup_code: Optional[str] = None
    session_token: str


# Email-based 2FA Models
class EmailTwoFactorSetupResponse(BaseModel):
    setup_required: bool = True
    email_address: Optional[str] = None
    message: str


class EmailTwoFactorVerifyRequest(BaseModel):
    email_code: str
    session_token: str


# User Management Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="User's email address for 2FA")
    phone: str = Field(
        ..., min_length=10, max_length=15, description="User's phone number"
    )
    pin: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="10-digit PIN for authentication",
    )
    pin_hash: str = Field(..., description="Bcrypt hashed PIN")
    permissions: dict = Field(
        default_factory=dict,
        description="User permissions for tabs and fields",
    )
    is_active: bool = Field(
        default=True, description="Whether user account is active"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )


class UserCreate(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="User's email address for 2FA")
    phone: str = Field(
        ..., min_length=10, max_length=15, description="User's phone number"
    )
    pin: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="10-digit PIN for authentication",
    )
    permissions: dict = Field(
        default_factory=dict,
        description="User permissions for tabs and fields",
    )


class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    pin: Optional[str] = None
    permissions: Optional[dict] = None
    is_active: Optional[bool] = None
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )


# Test Record Models
class TestRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    test_type: str = Field(
        ..., description="Type of test: HIV, HCV, Bloodwork"
    )
    test_date: Optional[str] = None
    # HIV-specific fields
    hiv_result: Optional[str] = None  # negative/positive
    hiv_type: Optional[str] = None  # Type 1/Type 2
    hiv_tester: Optional[str] = Field(default="CM")  # Tester initials
    # HCV-specific fields
    hcv_result: Optional[str] = None  # negative/positive
    hcv_tester: Optional[str] = Field(default="CM")  # Tester initials
    # Bloodwork-specific fields
    bloodwork_type: Optional[str] = None  # DBS/Serum
    bloodwork_circles: Optional[str] = None  # 1-5 for DBS
    bloodwork_result: Optional[str] = (
        None  # Pending/Submitted/Positive/Negative
    )
    bloodwork_date_submitted: Optional[str] = None
    bloodwork_tester: Optional[str] = Field(default="CM")  # Tester initials
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class TestRecordCreate(BaseModel):
    test_type: str = Field(
        ..., description="Type of test: HIV, HCV, Bloodwork"
    )
    test_date: Optional[str] = None
    # HIV-specific fields
    hiv_result: Optional[str] = None
    hiv_type: Optional[str] = None
    hiv_tester: Optional[str] = Field(default="CM")
    # HCV-specific fields
    hcv_result: Optional[str] = None
    hcv_tester: Optional[str] = Field(default="CM")
    # Bloodwork-specific fields
    bloodwork_type: Optional[str] = None
    bloodwork_circles: Optional[str] = None
    bloodwork_result: Optional[str] = None
    bloodwork_date_submitted: Optional[str] = None
    bloodwork_tester: Optional[str] = Field(default="CM")


class TestRecordUpdate(BaseModel):
    test_type: Optional[str] = None
    test_date: Optional[str] = None
    hiv_result: Optional[str] = None
    hiv_type: Optional[str] = None
    hiv_tester: Optional[str] = None
    hcv_result: Optional[str] = None
    hcv_tester: Optional[str] = None
    bloodwork_type: Optional[str] = None
    bloodwork_circles: Optional[str] = None
    bloodwork_result: Optional[str] = None
    bloodwork_date_submitted: Optional[str] = None
    bloodwork_tester: Optional[str] = None


class NotesRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    noteDate: str = Field(..., description="Date of the note")
    noteText: str = Field(..., description="Note content")
    templateType: Optional[str] = Field(
        default="General Note", description="Type of template used"
    )
    noteTime: Optional[str] = Field(
        default_factory=lambda: datetime.now(
            pytz.timezone("America/Toronto")
        ).strftime("%H:%M")
    )
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )


class NotesCreate(BaseModel):
    noteDate: str = Field(..., description="Date of the note")
    noteText: str = Field(..., description="Note content")
    templateType: Optional[str] = Field(
        default="General Note", description="Type of template used"
    )


class NotesUpdate(BaseModel):
    noteDate: Optional[str] = None
    noteText: Optional[str] = None
    templateType: Optional[str] = None


# Medication Record Models
class MedicationRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    medication: str = Field(
        ..., description="Medication name: Epclusa, Maviret, Vosevi"
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    outcome: str = Field(
        ...,
        description="Outcome: Active, Completed, Non Compliance, Side Effect, Did not start, Death",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )


class MedicationCreate(BaseModel):
    medication: str = Field(
        ..., description="Medication name: Epclusa, Maviret, Vosevi"
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    outcome: str = Field(
        ...,
        description="Outcome: Active, Completed, Non Compliance, Side Effect, Did not start, Death",
    )


class MedicationUpdate(BaseModel):
    medication: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    outcome: Optional[str] = None


# Interaction Record Models
class InteractionRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    date: Optional[str] = None
    description: str = Field(
        ...,
        description="Description: Screening, Adherence, Bloodwork, Discretionary, Referral, Consultation, Outreach, Repeat, Results, Safe Supply, Lab Req, Telephone, Remittance, Update, Counselling, Trillium, Housing, SOT, EOT, SVR, Locate, Staff",
    )
    referral_id: Optional[str] = None
    amount: Optional[str] = None
    payment_type: Optional[str] = None
    issued: str = Field(default="Select", description="Issued: Yes, No")
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )


class InteractionCreate(BaseModel):
    date: str = Field(..., description="Interaction date")
    description: str = Field(..., description="Interaction description")
    referral_id: Optional[str] = None
    amount: Optional[str] = None
    payment_type: Optional[str] = None
    issued: str = Field(default="Select", description="Issued: Yes, No")


class InteractionUpdate(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    referral_id: Optional[str] = None
    amount: Optional[str] = None
    payment_type: Optional[str] = None
    issued: Optional[str] = None


# Dispensing Record Models
class DispensingRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    medication: str = Field(
        ..., description="Medication name: Epclusa, Maviret, Vosevi"
    )
    rx: Optional[str] = None
    quantity: str = Field(default="28", description="Quantity - default 28")
    lot: Optional[str] = None
    product_type: str = Field(
        default="Commercial",
        description="Product Type: Commercial, Compassionate",
    )
    expiry_date: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )


class DispensingCreate(BaseModel):
    medication: str = Field(
        ..., description="Medication name: Epclusa, Maviret, Vosevi"
    )
    rx: Optional[str] = None
    quantity: str = Field(default="28", description="Quantity - default 28")
    lot: Optional[str] = None
    product_type: str = Field(
        default="Commercial",
        description="Product Type: Commercial, Compassionate",
    )
    expiry_date: Optional[str] = None


class DispensingUpdate(BaseModel):
    medication: Optional[str] = None
    rx: Optional[str] = None
    quantity: Optional[str] = None
    lot: Optional[str] = None
    product_type: Optional[str] = None
    expiry_date: Optional[str] = None


# Activity Record Models
class ActivityRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    registration_id: str = Field(
        ..., description="Reference to the main registration"
    )
    date: str = Field(..., description="Activity date - defaults to today")
    time: Optional[str] = None
    description: str = Field(..., description="Activity description")
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone("US/Eastern"))
        .isoformat()
    )


class ActivityCreate(BaseModel):
    date: str = Field(..., description="Activity date - defaults to today")
    time: Optional[str] = None
    description: str = Field(..., description="Activity description")


class ActivityUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    description: Optional[str] = None


class ChartRequest(BaseModel):
    chart_type: str = Field(
        ...,
        description="Type of chart: 'monthly_trend', 'disposition_bar', 'yearly_comparison'",
    )
    title: Optional[str] = Field(default="Data Analysis Chart")
    download: Optional[bool] = Field(
        default=False, description="Return downloadable image"
    )


class ChartResponse(BaseModel):
    chart_html: Optional[str] = None
    chart_image_url: Optional[str] = None
    chart_data: dict


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


class DataSummaryResponse(BaseModel):
    total_records: int
    date_range: dict
    top_dispositions: List[dict]
    upload_info: dict


# Clinical Summary Template Models
class ClinicalTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Template name (e.g., "Positive", "Negative - Pipes")
    content: str  # Template content
    is_default: bool = Field(
        default=False
    )  # Whether this is a default template
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ClinicalTemplateCreate(BaseModel):
    name: str
    content: str
    is_default: bool = Field(default=False)


class ClinicalTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Notes Template Models (identical structure to Clinical Templates)
class NotesTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Template name (e.g., "Consultation", "Lab", "Prescription")
    content: str  # Template content
    is_default: bool = Field(
        default=False
    )  # Whether this is a default template
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotesTemplateCreate(BaseModel):
    name: str
    content: str
    is_default: bool = Field(default=False)


class NotesTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Disposition Models (similar to Templates but simpler)
class Disposition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Disposition name (e.g., "ACTIVE", "PENDING")
    is_frequent: bool = Field(
        default=False
    )  # Whether this is a frequently used disposition
    is_default: bool = Field(
        default=False
    )  # Whether this is a default disposition
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DispositionCreate(BaseModel):
    name: str
    is_frequent: bool = Field(default=False)
    is_default: bool = Field(default=False)


class DispositionUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Referral Site Models (similar to Dispositions)
class ReferralSite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Referral site name (e.g., "Barrie - City Centre Pharmacy")
    is_frequent: bool = Field(
        default=False
    )  # Whether this is a frequently used referral site
    is_default: bool = Field(
        default=False
    )  # Whether this is a default referral site
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralSiteCreate(BaseModel):
    name: str
    is_frequent: bool = Field(default=False)
    is_default: bool = Field(default=False)


class ReferralSiteUpdate(BaseModel):
    name: Optional[str] = None
    is_frequent: Optional[bool] = None
    is_default: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Sharing models
class ShareAttachmentRequest(BaseModel):
    attachment_data: dict
    expires_in_minutes: int = 30


class ShareAttachmentResponse(BaseModel):
    share_id: str
    share_url: str
    preview_url: str
    expires_at: str
    expires_in_minutes: int

    # AI Assistant Models


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="Role of the message sender (user/assistant)"
    )
    content: str = Field(..., description="Content of the message")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(
            pytz.timezone("America/Toronto")
        ).isoformat()
    )


class ChatQuery(BaseModel):
    message: str = Field(
        ..., description="User's query about registration data"
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Chat session identifier",
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    session_id: str = Field(..., description="Chat session identifier")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(
            pytz.timezone("America/Toronto")
        ).isoformat()
    )
