# app/schemas.py
from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)
from datetime import date


class ContactMessageCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=10, max_length=1000)


class RegistrationMessageCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    dob: date
    health_card_number: Optional[str] = Field(
        None, min_length=10, max_length=12
    )
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    consent_given: bool = Field(..., description="User must give consent")
