# app/config.py
import logging
from typing import Any, List
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
    # JWT
    jwt_access_secret: str = get_env("JWT_ACCESS_SECRET")
    jwt_refresh_secret: str = get_env("JWT_REFRESH_SECRET")
    jwt_algorithm: str = get_env("JWT_ALGORITHM")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    temp_login_expire_minutes: int = 5
    reset_pw_expire_hours: int = 1
    verify_email_expire_day: int = 1

    # MFA
    mfa_secret_key: str = get_env("MFA_ENCRYPTION_KEY")
    email_mfa_expire_minutes: int = 5

    # Database
    database_url: str = get_env("DATABASE_URL")
    host: str = get_env("POSTGRES_HOST")
    user: str = get_env("POSTGRES_USER")
    password: str = get_env("POSTGRES_PASSWORD")
    db: str = get_env("POSTGRES_DB")

    # CORS
    allowed_origins: List[str] = get_env("ALLOWED_ORIGINS")

    # App
    app_url: str = get_env("APP_URL")
    app_name: str = get_env("APP_NAME")
    debug: bool = os.getenv("DEBUG") == "True"

    # Email
    email: str = get_env("SMTP_EMAIL")
    email_pw: str = get_env("SMTP_PASSWORD")

    # database
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.getenv("DB_NAME", "my420_ca_db")

    # claude
    anthropic_key = get_env("ANTHROPIC_API_KEY")
    anthropic_client = AsyncAnthropic(api_key=anthropic_key)
    anthropic_max_tokens = os.getenv("MAX_TOKENS", 1024)
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    support_email = get_env("SUPPORT_EMAIL")
    ######### OLD ######
    #
    # # environment
    # environment = os.getenv("ENVIRONMENT", "production").lower()
    #
    # # authentication
    # TOTP_ENCRYPTION_KEY = os.getenv(
    #     "TOTP_ENCRYPTION_KEY",
    #     Fernet.generate_key(),
    # )
    # cipher_suite = Fernet(TOTP_ENCRYPTION_KEY)
    # admin_2fa_email = os.getenv("ADMIN_2FA_EMAIL", "support@my420.ca")
    #
    # # smtp
    # smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    # smtp_port = int(os.getenv("SMTP_PORT", "587"))
    # smtp_username = os.getenv("SMTP_USERNAME", "")
    # smtp_password = os.getenv("SMTP_PASSWORD", "")


settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
