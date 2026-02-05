from asyncpg.exceptions import UniqueViolationError
from app.core.authentication.services import (
    EmailMfaCodeService,
    TokenService,
    UserService,
)
from app.core.authentication.schemas import (
    Email,
    ForgotPassword,
    RegisterRequest,
    UserCreate,
    UserRead,
    UserResponse,
    VerificationToken,
)
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from app.common.crypt import SecurityService
from app.common.config import settings
from app.common.dependencies import get_current_user
import datetime as dt
from app.common.storage.postgres import database
from datetime import timezone
from app.common.storage.redis import redis_client
from app.webpage.schema import ContactMessageCreate, RegistrationMessageCreate
from app.webpage.services import ContactService, RegisterService

# from app.core.zoom.services import ZoomService

router = APIRouter(prefix="/testing", tags=["Testing"])


async def register_user(data: RegisterRequest) -> UserResponse:
    password_hash = SecurityService.hash_password(data.password)

    insert_query = """
    INSERT INTO users (email, password_hash, is_verified, role, location_permissions)
    VALUES ($1, $2, $3, 'admin', ARRAY['All'])
    RETURNING id;
    """

    select_query = """
    SELECT id, email, authenticator_mfa_enabled, created_at, last_login
    FROM users
    WHERE id = $1;
    """

    # Insert user and get the generated ID
    async with database.get_transaction() as conn:
        row = await conn.fetchrow(
            insert_query, data.email, password_hash, True
        )
        user_id = row["id"]

    # Fetch the full user record
    async with database.get_connection() as conn:
        user_row = await conn.fetchrow(select_query, user_id)
        return UserResponse(**dict(user_row))


@router.post("/register")
async def test_register(data: RegisterRequest):
    if await UserService.check_user_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Create user
    # user = await UserService.register_user(data.email, data.password)
    user = await register_user(data)

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


@router.post("/users")
async def create_user(
    new_user: UserCreate,
    user: UserRead = Depends(get_current_user),
):
    if await UserService.check_user_exists(new_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Create user
    id = await UserService.create_user(new_user)

    if not id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error creating user.",
        )

    return {
        "id": id,
        "message": "Registration successful. Check your email to verify.",
    }


@router.post("/contact-message", response_model=dict)
async def submit_contact_message(message: ContactMessageCreate):

    id = await ContactService.create_contact_message(message)

    if not id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact message not created.",
        )

    return {
        "message": "Contact successful sent.",
        "contact_id": id,
        "status": "pending",
    }


@router.post("/register-message", response_model=dict)
async def register_for_testing(registration: RegistrationMessageCreate):
    # Send contact email to support team

    try:
        id = await RegisterService.create_register_message(registration)

        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Register message not created.",
            )

        return {
            "message": "Registration successful",
            "registration_id": id,
            "status": "pending",
        }
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Health card number {registration.health_card_number} already registered.",
        )
    except Exception as e:
        # Catch any other exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


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


@router.post("/expire-zoom-session/{patient_id}")
async def expire_session(patient_id: int):
    past_time = datetime.now(timezone.utc) - timedelta(days=1)

    redis = redis_client.get_client()
    await redis.hset(
        f"session:metadata:{patient_id}",
        "host_last_seen_at",
        past_time.isoformat(),
    )

    return {"message": "Expired session successfully"}
