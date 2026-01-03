from app.email.messages import (
    ContactEmailMessage,
    RegistrationEmailMessage,
)
from app.email.service import EmailService
from app.config import settings


def send_contact_email(contact_data):
    """Send contact message to support email"""
    subject = f"New Contact Message - {contact_data.get('subject', 'General Inquiry')} - my420.ca"

    (
        EmailService()
        .recipient(settings.support_email)
        .subject(subject)
        .body(ContactEmailMessage(contact_data))
        .send()
    )


def send_registration_email(registration_data):
    """Send registration details to support email"""
    subject = "New Testing Registration - my420.ca"

    (
        EmailService()
        .recipient(settings.support_email)
        .subject(subject)
        .body(RegistrationEmailMessage(registration_data))
        .send()
    )
