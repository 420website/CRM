from email.mime.multipart import MIMEMultipart
import base64
from email.mime.text import MIMEText
import io
import logging
import smtplib
from typing import List, Optional
import uuid
import pyotp
import pytz
import qrcode
import bcrypt
import secrets
from datetime import datetime
from app.database import db
from app.config import settings


# EMAIL-BASED 2FA UTILITY FUNCTIONS
async def get_admin_user():
    """Get or create admin user document"""
    admin_user = await db.admin_users.find_one({"username": "admin"})
    if not admin_user:
        # Create default admin user with existing PIN
        default_pin = "0224"
        pin_hash = bcrypt.hashpw(
            default_pin.encode(), bcrypt.gensalt()
        ).decode()

        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "pin_hash": pin_hash,
            "two_fa_enabled": False,
            "two_fa_email": None,
            "email_code": None,
            "email_code_expires": None,
            "failed_2fa_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "current_session_token": None,
            "session_expires": None,
        }
        await db.admin_users.insert_one(admin_user)
    return admin_user


def generate_email_code() -> str:
    """Generate a 6-digit email verification code"""
    return f"{secrets.randbelow(1000000):06d}"


def hash_email_code(code: str) -> str:
    """Hash email verification code for secure storage"""
    return bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()


def verify_email_code_hash(stored_hash: str, provided_code: str) -> bool:
    """Verify email verification code against stored hash"""
    return bcrypt.checkpw(provided_code.encode(), stored_hash.encode())


async def send_2fa_email(email: str, code: str) -> bool:
    """Send 2FA verification code via email"""
    try:
        # Get email configuration from environment (same as existing email system)
        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password

        if not smtp_password:
            logging.error("SMTP_PASSWORD not configured")
            return False

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = email
        msg["Subject"] = "Login - Verification Code"

        # Email body with verification code
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333; text-align: center; margin-bottom: 30px; line-height: 1.2;">
                    🔐 Login<br>Verification
                </h2>
                
                <div style="background-color: white; padding: 25px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <p style="font-size: 16px; color: #555; margin-bottom: 20px;">
                        Your login code is:
                    </p>
                    
                    <div style="background-color: #000; color: white; font-size: 32px; font-weight: bold; padding: 15px 30px; border-radius: 8px; letter-spacing: 8px; font-family: 'Courier New', monospace; white-space: nowrap; display: inline-block;">
                        {code}
                    </div>
                    
                    <p style="font-size: 14px; color: #888; margin-top: 20px;">
                        This code expires in <strong>3 minutes</strong>
                    </p>
                </div>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>⚠️ Security Notice:</strong> If you didn't request this code, please ignore this email. Never share this code with anyone.
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #888; text-align: center; margin-top: 30px;">
                    420 Program<br>
                    Automated message - do not reply
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()

        logging.info(f"2FA email sent successfully to {email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send 2FA email: {str(e)}")
        return False


def is_email_code_expired(expires_at: Optional[datetime]) -> bool:
    """Check if email verification code has expired"""
    if not expires_at:
        return True

    toronto_tz = pytz.timezone("America/Toronto")
    current_time = datetime.now(toronto_tz)

    if isinstance(expires_at, str):
        # Parse string datetime and make it timezone-aware
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if expires_at.tzinfo is None:
            expires_at = toronto_tz.localize(expires_at)
    elif isinstance(expires_at, datetime) and expires_at.tzinfo is None:
        # Make naive datetime timezone-aware
        expires_at = toronto_tz.localize(expires_at)

    return current_time > expires_at


# LEGACY TOTP FUNCTIONS (DEPRECATED - FOR BACKWARD COMPATIBILITY ONLY)
def generate_totp_secret():
    """DEPRECATED: Generate a new TOTP secret"""
    return pyotp.random_base32()


def encrypt_totp_secret(secret: str) -> str:
    """DEPRECATED: Encrypt TOTP secret for database storage"""
    return settings.cipher_suite.encrypt(secret.encode()).decode()


def decrypt_totp_secret(encrypted_secret: str) -> str:
    """DEPRECATED: Decrypt TOTP secret for verification"""
    return settings.cipher_suite.decrypt(encrypted_secret.encode()).decode()


def generate_qr_code(secret: str, username: str = "admin") -> str:
    """DEPRECATED: Generate QR code for TOTP setup"""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username, issuer_name="Medical Platform Admin"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for frontend display
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_base64}"


def generate_backup_codes(count: int = 10) -> List[str]:
    """DEPRECATED: Generate backup codes for 2FA recovery"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def hash_backup_codes(codes: List[str]) -> List[str]:
    """DEPRECATED: Hash backup codes for secure storage"""
    return [
        bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        for code in codes
    ]


def verify_totp_code(
    secret: str, code: str, last_used: Optional[datetime] = None
) -> bool:
    """DEPRECATED: Verify TOTP code with replay attack prevention"""
    totp = pyotp.TOTP(secret)

    # Check if code is valid (30-second window, ±1 period tolerance)
    if not totp.verify(code, valid_window=1):
        return False

    # Prevent replay attacks - check if this exact time window was used
    current_time = datetime.now()
    if last_used:
        # If last use was within the same 30-second window, reject
        time_diff = (current_time - last_used).total_seconds()
        if time_diff < 30:
            return False

    return True


def verify_backup_code(
    stored_codes: List[str], provided_code: str
) -> tuple[bool, List[str]]:
    """Verify backup code and remove it from available codes"""
    for i, stored_hash in enumerate(stored_codes):
        if bcrypt.checkpw(provided_code.encode(), stored_hash.encode()):
            # Remove used backup code
            remaining_codes = stored_codes.copy()
            remaining_codes.pop(i)
            return True, remaining_codes
    return False, stored_codes
