# app/config.py
import logging
from typing import Any
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from anthropic import AsyncAnthropic

load_dotenv()


def get_env(key: str) -> Any:
    value = os.getenv(key)

    if value is None:
        raise ValueError(f"Environment variable {key} not found.")
    return value


class Settings:
    # database
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "my420_ca_db")

    # claude
    anthropic_key = get_env("ANTHROPIC_API_KEY")
    anthropic_client = AsyncAnthropic(api_key=anthropic_key)

    # environment
    environment = os.getenv("ENVIRONMENT", "production").lower()

    # authentication
    TOTP_ENCRYPTION_KEY = os.getenv(
        "TOTP_ENCRYPTION_KEY",
        Fernet.generate_key(),
    )
    cipher_suite = Fernet(TOTP_ENCRYPTION_KEY)
    support_email = os.getenv("SUPPORT_EMAIL", "420pharmacyprogram@gmail.com")
    admin_2fa_email = os.getenv("ADMIN_2FA_EMAIL", "support@my420.ca")

    # smtp
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")


settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
