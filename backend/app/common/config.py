# app/config.py
# import logging
from typing import Any, List
import os
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()


def get_env(key: str) -> Any:
    value = os.getenv(key)

    if value is None:
        raise ValueError(f"Environment variable {key} not found.")
    return value


class Settings:
    # Zoom
    sdk_key: str = get_env("ZOOM_VIDEO_SDK_KEY")
    sdk_secret: str = get_env("ZOOM_VIDEO_SDK_SECRET")
    api_key: str = get_env("ZOOM_API_KEY")
    api_secret: str = get_env("ZOOM_API_SECRET")
    host_grace_seconds = 180

    # JWT
    jwt_algorithm: str = get_env("JWT_ALGORITHM")
    jwt_access_secret: str = get_env("JWT_ACCESS_SECRET")
    access_token_expire_minutes: int = 30
    share_link_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    temp_login_expire_minutes: int = 5
    reset_pw_expire_hours: int = 1
    verify_email_expire_day: int = 1

    # MFA
    mfa_secret_key: str = get_env("MFA_ENCRYPTION_KEY")
    email_mfa_expire_minutes: int = 5

    # CORS
    allowed_origins: List[str] = get_env("ALLOWED_ORIGINS").split(",")

    # app
    app_url: str = get_env("APP_URL")
    app_name: str = get_env("APP_NAME")
    debug: bool = os.getenv("DEBUG") == "true"
    environment: str = os.getenv("ENVIRONMENT", "Production")
    support_email = get_env("SUPPORT_EMAIL")
    is_my420: bool = get_env("IS_MY420") == "true"

    # smtp
    email: str = get_env("SMTP_EMAIL")
    email_pw: str = get_env("SMTP_PASSWORD")
    email_provider: str = get_env("SMTP_SERVER")

    # claude
    anthropic_key = get_env("ANTHROPIC_API_KEY")
    anthropic_client = AsyncAnthropic(api_key=anthropic_key)
    anthropic_max_tokens = int(os.getenv("MAX_TOKENS", 1024))
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    system_prompt: list | None = None

    # postgres
    pg_url: str = get_env("POSTGRES_URL")
    pg_host: str = get_env("POSTGRES_HOST")
    pg_user: str = get_env("POSTGRES_USER")
    pg_password: str = get_env("POSTGRES_PASSWORD")
    pg_db: str = get_env("POSTGRES_DB")
    ca_file: str = os.getenv("CA_FILE", "/certs/ca-chain.crt")

    # mongodb
    mongo_url: str = get_env("MONGODB_URL")
    mongo_name: str = get_env("MONGODB_NAME")

    # redis
    max_chat_length = 10
    chat_history_ttl = 20 * 60
    redis_host = get_env("REDIS_HOST")
    redis_port = get_env("REDIS_PORT")
    redis_password = get_env("REDIS_PASSWORD")

    # minio
    minio_key_id: str = get_env("MINIO_ROOT_USER")
    minio_access_key: str = get_env("MINIO_ROOT_PASSWORD")
    minio_url: str = get_env("MINIO_SERVER_URL")
    minio_verify: str | bool = os.getenv("MINIO_VERIFY", False)
    minio_signature_version: str = os.getenv("MINIO_SIGNATURE_VERSION", "s3v4")
    minio_addressing_style: str = os.getenv("MINIO_ADDRESSING_STYLE", "path")


settings = Settings()
