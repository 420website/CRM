from app.config import settings
from app.email.service import HtmlMessage
from datetime import datetime


def load_email_template(template_path):
    with open(template_path, "r") as f:
        return f.read()


class ResetPasswordMessage(HtmlMessage):
    def __init__(self, reset_url: str) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/crm/reset_password.html"
        )
        body = html_template.replace("{{RESET_URL}}", reset_url)
        self.msg = body


class VerifyEmailMessage(HtmlMessage):
    def __init__(self, verification_url: str) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/crm/verify_email.html"
        )
        body = html_template.replace("{{VERIFICATION_URL}}", verification_url)
        self.msg = body


class MfaEmailMessage(HtmlMessage):
    def __init__(self, verification_code: str) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/crm/mfa_code.html"
        )
        body = html_template.replace(
            "{{VERIFICATION_CODE}}", verification_code
        )
        self.msg = body


class ContactEmailMessage(HtmlMessage):
    def __init__(self, contact_data: dict) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/my420/contact_email.html"
        )

        body = html_template
        placeholders = {
            "FIRST": contact_data.get("first_name", "N/A"),
            "LAST": contact_data.get("last_name", "N/A"),
            "EMAIL": contact_data.get("email", "N/A"),
            "SUBJECT": contact_data.get("subject", "General Inquiry"),
            "SUBMITTED_AT": contact_data.get(
                "submitted_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            "MESSAGE": contact_data.get("message", "No message provided"),
        }

        for key, value in placeholders.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))

        self.msg = body


class RegistrationEmailMessage(HtmlMessage):
    def __init__(self, contact_data: dict) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/my420/registration_email.html"
        )

        body = html_template
        placeholders = {
            "FIRST": contact_data.get("first_name", "N/A"),
            "LAST": contact_data.get("last_name", "N/A"),
            "DOB": contact_data.get("dob", "N/A"),
            "HEALTH_CARD": contact_data.get(
                "health_card_number", "Not Provided"
            ),
            "PHONE_NUM": contact_data.get("phone_number", "Not Provided"),
            "EMAIL": contact_data.get("email", "Not Provided"),
            "REGISTRATION_DATE": contact_data.get(
                "regisration_date",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
            "CONSENT": contact_data.get("consent_given", "No"),
        }

        for key, value in placeholders.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))

        self.msg = body


class FinalizedEmailMessage(HtmlMessage):
    def __init__(self, registration_data: dict) -> None:
        super().__init__()
        html_template = load_email_template(
            "app/email/templates/crm/finalized_email.html"
        )

        placeholders = {
            "REG_DATE": registration_data.get("reg_date", "Not provided"),
            "FINALIZED_AT": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "FIRST_NAME": registration_data.get("first_name", "N/A"),
            "LAST_NAME": registration_data.get("last_name", "N/A"),
            "DOB": registration_data.get("dob", "Not provided"),
            "AGE": registration_data.get("age", "Not provided"),
            "GENDER": registration_data.get("gender", "Not provided"),
            "HEALTH_CARD": registration_data.get(
                "health_card", "Not provided"
            ),
            "HEALTH_CARD_VERSION": registration_data.get(
                "health_card_version", "Not provided"
            ),
            "PHONE1": registration_data.get("phone1", "Not provided"),
            "PHONE2": registration_data.get("phone2", "Not provided"),
            "EMAIL": registration_data.get("email", "Not provided"),
            "ADDRESS": registration_data.get("address", "Not provided"),
            "CITY": registration_data.get("city", "Not provided"),
            "PROVINCE": registration_data.get("province", "Not provided"),
            "POSTAL_CODE": registration_data.get(
                "postal_code", "Not provided"
            ),
            "PATIENT_CONSENT": registration_data.get(
                "patient_consent", "Not provided"
            ),
            "DISPOSITION": registration_data.get(
                "disposition", "Not provided"
            ),
            "REFERRAL_SITE": registration_data.get(
                "referral_site", "Not provided"
            ),
            "PHYSICIAN": registration_data.get("physician", "Not specified"),
            "LANGUAGE": registration_data.get("language", "Not provided"),
            "SPECIAL_ATTENTION": registration_data.get(
                "special_attention", "None"
            ),
            "INSTRUCTIONS": registration_data.get("instructions", "None"),
            "SUMMARY_TEMPLATE": registration_data.get(
                "summary_template", "None provided"
            ),
            "SUPPORT_EMAIL": settings.email,
        }

        body = html_template
        for key, value in placeholders.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))

        self.msg = body
