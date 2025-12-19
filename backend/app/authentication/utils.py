# app/auth.py
from jose import JWTError, jwt
from argon2 import PasswordHasher
from datetime import datetime, timedelta
import datetime as dt
import string
import pyotp
import qrcode
import random
from io import BytesIO
import base64
import secrets
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from cryptography.fernet import Fernet
from argon2.exceptions import VerifyMismatchError

from app.authentication.schemas import RefreshToken, VerificationToken
from app.config import settings


ph = PasswordHasher()


class SecurityService:
    # Password handling
    @staticmethod
    def hash_password(password: str) -> str:
        return ph.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    # MFA handling
    @staticmethod
    def generate_email_mfa_code() -> str:
        """Generate a 6-digit random code for email MFA"""
        return "".join([str(random.randint(0, 9)) for _ in range(6)])

    @staticmethod
    def generate_mfa_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def encrypt_mfa_secret(secret: str) -> str:
        f = Fernet(settings.mfa_secret_key)
        return f.encrypt(secret.encode()).decode()

    @staticmethod
    def decrypt_mfa_secret(encrypted_secret: str) -> str:
        f = Fernet(settings.mfa_secret_key)
        return f.decrypt(encrypted_secret.encode()).decode()

    @staticmethod
    def generate_qr_code(email: str, secret: str) -> str:
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email, issuer_name=settings.app_name
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except Exception:
            return False

    @staticmethod
    def generate_recovery_codes(count: int = 10) -> List[str]:
        """Generate recovery codes"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes (easier to read than hex)
            code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(8)
            )
            codes.append(code)
        return codes

    # JWT Handling
    @staticmethod
    def generate_jwt(
        user_id: int,
        expires_delta: timedelta,
        auth: bool,
    ) -> Tuple[str, datetime]:
        expiry = datetime.now(dt.timezone.utc) + expires_delta

        payload: Dict[str, Any] = {"sub": str(user_id), "auth": auth}
        payload.update({"exp": int(expiry.timestamp())})
        payload.update({"iat": int(datetime.now(dt.timezone.utc).timestamp())})

        return (
            jwt.encode(
                payload,
                settings.jwt_access_secret,
                algorithm=settings.jwt_algorithm,
            ),
            expiry,
        )

    @staticmethod
    def decode_jwt(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_access_secret,
                algorithms=settings.jwt_algorithm,
            )
            payload["sub"] = int(payload["sub"])
            return payload
        except JWTError:
            return None

    # JWT Handling
    @staticmethod
    def generate_zoom_jwt(user_id: str, config: dict) -> Tuple[str, datetime]:
        expiry = datetime.now(dt.timezone.utc) + timedelta(minutes=30)
        exp = int(expiry.timestamp())
        iat = int(datetime.now(dt.timezone.utc).timestamp())

        payload: Dict[str, Any] = {
            "app_key": settings.sdk_key,
            "role_type": (1 if user_id == str(config["host_id"]) else 0),
            "tpc": config["session_name"],
            "version": 1,
            "exp": exp,
            "iat": iat,
            "video_webrtc_mode": 1,
            "user_identity": user_id,
            # "telemetry_tracking_id": "telemetryTrackingId",
        }

        return (
            jwt.encode(
                payload,
                settings.sdk_secret,
                algorithm=settings.jwt_algorithm,
            ),
            expiry,
        )

    @staticmethod
    def decode_zoom_jwt(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                settings.sdk_secret,
                algorithms=settings.jwt_algorithm,
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a 256-bit cryptographically secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_secure_token(token: str, hash: str) -> bool:
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        return hashed_token == hash

    @staticmethod
    def is_expired(token: Union[VerificationToken, RefreshToken]) -> bool:
        if token.expires_at < dt.datetime.now(dt.timezone.utc):
            return True
        return False
