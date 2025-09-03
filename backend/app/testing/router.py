from app.authentication.services import (
    EmailMfaCodeService,
    TokenService,
    UserService,
)
from app.authentication.schemas import (
    Email,
    ForgotPassword,
    RegisterRequest,
    UserRead,
    UserResponse,
    VerificationToken,
)
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from app.authentication.utils import SecurityService
from app.config import settings
from app.dependencies import get_current_user
import datetime as dt

router = APIRouter(prefix="/testing", tags=["Testing"])


@router.post("/register")
async def test_register(data: RegisterRequest):
    if await UserService.check_user_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Create user
    user = await UserService.register_user(data.email, data.password)

    # Token to verify
    token = SecurityService.generate_secure_token()

    verification_token = VerificationToken(
        id=None,
        user_id=user.id,
        token_hash=SecurityService.hash_token(token),
        token_type="email_verification",
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(days=settings.verify_email_expire_day),
    )
    await TokenService.create_verification_token(verification_token)

    return {"message": "Registration successful.", "token": token}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    user = await UserService.get_user_by_email(data.email)
    if not user:
        return {"message": "If email exists, reset link sent"}

    token = SecurityService.generate_secure_token()
    reset_token = VerificationToken(
        id=None,
        user_id=user.id,
        token_hash=SecurityService.hash_token(token),
        token_type="password_reset",
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(hours=settings.reset_pw_expire_hours),
    )

    await TokenService.create_verification_token(reset_token)

    return {"message": "If email exists reset link sent.", "token": token}


@router.post("/send-verification")
async def send_verification(email: Email):
    user = await UserService.get_user_by_email(email.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email.",
        )

    await TokenService.delete_verification_token(user.id)

    # Token to verify
    token = SecurityService.generate_secure_token()

    verification_token = VerificationToken(
        id=None,
        user_id=user.id,
        token_hash=SecurityService.hash_token(token),
        token_type="email_verification",
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(days=settings.verify_email_expire_day),
    )
    await TokenService.create_verification_token(verification_token)

    return {"message": "If email exists reset link sent.", "token": token}


@router.post("/send-mfa-email")
async def send_mfa_email(email: Email):
    user = await UserService.get_user_by_email(email.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email.",
        )
    code = await EmailMfaCodeService.create_email_mfa_code(
        user.id, timedelta(minutes=settings.email_mfa_expire_minutes)
    )

    return {
        "message": "MFA code sent successful. Check your email to verify.",
        "code": code,
    }


@router.post("/delete-user")
async def delete_user(user_data: RegisterRequest):
    if not await UserService.check_user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    await UserService.delete_user(user_data.email, user_data.password)

    return {"message": "User deleted  successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserRead = Depends(get_current_user)):
    return current_user
