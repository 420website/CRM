# app/schemas.py
from datetime import timezone
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import List, Literal, Optional
import phonenumbers


# Api objects
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginPin(BaseModel):
    password: str


class LoginResponse(BaseModel):
    access_token: str
    authenticator_mfa_setup: bool = False
    mfa_required: bool = True
    expires_at: datetime
    token_type: str = "bearer"


class Email(BaseModel):
    email: EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str


class MFAVerfiedResponse(BaseModel):
    recovery_codes: Optional[List[str]]
    access_token: str
    expires_at: datetime
    user_role: str
    user_permissions: List[str]
    token_type: str = "bearer"


class MFAVerifiactionCode(BaseModel):
    code: str


class MFARecoveryCode(BaseModel):
    code: str


class RecoveryCodes(BaseModel):
    codes: List[str]


class RecoveryCode(BaseModel):
    id: int
    user_id: int
    code_hash: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password_hash: Optional[str] = None
    password: Optional[str] = None
    mfa_secret: Optional[str] = None
    is_verified: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    # email: Optional[str] = ""
    # authenticator_mfa_enabled: Optional[bool] = None
    # role: Optional[str] = None
    # permissions: Optional[List[str]] = None


class UserRead(UserBase):
    id: int
    email: str
    role: str
    permissions: List[str]
    authenticator_mfa_enabled: bool

    class Config:
        from_attributes = True  # For **dict conversion


class UserUpdate(UserBase):
    email: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    authenticator_mfa_enabled: Optional[bool] = None


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str
    authenticator_mfa_enabled: Optional[bool] = False
    mfa_secret: Optional[str] = None
    is_verified: Optional[bool] = False
    role: str
    permissions: List[str]

    @field_validator("phone_number")
    def validate_phone(cls, v: str) -> str:
        try:
            number = phonenumbers.parse(v, "US")
            if not phonenumbers.is_valid_number(number):
                raise ValueError("Invalid phone number")
            # format it consistently (e.g., E.164)
            return phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.E164
            )
        except Exception:
            raise ValueError("Invalid phone number format")


class UserResponse(BaseModel):
    id: int
    email: str
    authenticator_mfa_enabled: bool
    # role: str
    # permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# Refresh tokens
class RefreshToken(BaseModel):
    id: Optional[int] = None
    user_id: int
    token_hash: str
    expires_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("expires_at")
    def validate_expires_at(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class TokenResponse(BaseModel):
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"


class RefreshResponse(BaseModel):
    access_token: str
    expires_at: datetime
    user_role: str
    user_permissions: List[str]
    token_type: str = "bearer"


# verification tokens
class VerificationToken(BaseModel):
    id: Optional[int] = None
    user_id: int
    token_hash: str
    token_type: Literal["email_verification", "password_reset"]
    expires_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("expires_at")
    def validate_expires_at(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
