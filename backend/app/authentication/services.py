# import aiomysql
from typing import List, Optional, Union
from fastapi import HTTPException, status
from app.database import database
from app.authentication.schemas import (
    UserCreate,
    RefreshToken,
    TokenResponse,
    UserRead,
    UserResponse,
    UserUpdate,
    VerificationToken,
)
from fastapi import Response
from app.authentication.utils import SecurityService
import datetime as dt
from datetime import timedelta, datetime
from app.config import settings
from app.email.messages import (
    MfaEmailMessage,
    ResetPasswordMessage,
    VerifyEmailMessage,
)
from app.email.service import EmailService


async def update_response_refresh_token(user_id: int, response: Response):
    # Create Refresh token
    days_to_expire = settings.refresh_token_expire_days
    refresh_token = SecurityService.generate_secure_token()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=days_to_expire * 24 * 60 * 60,
        path="/",
    )

    # Add to database
    token = RefreshToken(
        id=None,
        user_id=user_id,
        token_hash=SecurityService.hash_token(refresh_token),
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(days=days_to_expire),
    )
    await TokenService.create_refresh_token(token)


async def send_verify_email_msg(user_id: int, email: str):
    # delete if any token exists
    await TokenService.delete_verification_token(user_id)

    # Token to verify
    token = SecurityService.generate_secure_token()

    verification_token = VerificationToken(
        id=None,
        user_id=user_id,
        token_hash=SecurityService.hash_token(token),
        token_type="email_verification",
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(days=settings.verify_email_expire_day),
    )
    await TokenService.create_verification_token(verification_token)

    # Send verification email
    verification_url = f"{settings.app_url}/verify-email?token={token}"
    (
        EmailService()
        .recipient(email)
        .subject("Verify Email")
        .body(VerifyEmailMessage(verification_url))
        .send()
    )


async def send_email_mfa_code_msg(user_id: int, email: str):
    code = await EmailMfaCodeService.create_email_mfa_code(
        user_id, timedelta(minutes=settings.email_mfa_expire_minutes)
    )

    (
        EmailService()
        .recipient(email)
        .subject("Verification Code")
        .body(MfaEmailMessage(code))
        .send()
    )


async def send_reset_password_msg(user_id: int, email: str):
    # delete if any token exists
    await TokenService.delete_verification_token(user_id)

    token = SecurityService.generate_secure_token()
    reset_token = VerificationToken(
        id=None,
        user_id=user_id,
        token_hash=SecurityService.hash_token(token),
        token_type="password_reset",
        expires_at=datetime.now(dt.timezone.utc)
        + timedelta(hours=settings.reset_pw_expire_hours),
    )

    await TokenService.create_verification_token(reset_token)

    # Send verification email
    reset_url = f"{settings.app_url}/reset-password?token={token}"
    (
        EmailService()
        .recipient(email)
        .subject("Reset Password")
        .body(ResetPasswordMessage(reset_url))
        .send()
    )


async def update_user_last_login(user_id: int):
    user_update = UserUpdate()
    user_update.last_login = dt.datetime.now(dt.timezone.utc)
    await UserService.update_user(user_id, user_update)


async def update_user_password(user_id: int, password: str):
    user_update = UserUpdate()
    user_update.password_hash = SecurityService.hash_password(password)
    await UserService.update_user(user_id, user_update)


async def update_user_is_verified(user_id: int, is_verified: bool):
    user_update = UserUpdate()
    user_update.is_verified = is_verified
    await UserService.update_user(user_id, user_update)


# Users
class UserService:
    # Helper methods
    @staticmethod
    async def validate_user(
        email: str,
        password: str,
    ) -> Union[UserRead, None]:
        user = await UserService.get_user_by_email(email)
        if user is None or user.password_hash is None:
            return None
        elif not SecurityService.verify_password(password, user.password_hash):
            return None
        else:
            return user

    @staticmethod
    async def validate_pin(password: str) -> Union[UserRead, None]:
        user = await UserService.get_user_by_pin(password)
        if user is None or user.password_hash is None:
            return None
        else:
            return user

    @staticmethod
    async def check_user_exists(email: str):
        user = await UserService.get_user_by_email(email)

        if user:
            return True
        else:
            return False

    # Services
    @staticmethod
    async def register_user(email: str, password: str) -> UserResponse:
        password_hash = SecurityService.hash_password(password)

        insert_query = """
        INSERT INTO users (email, password_hash, is_verified)
        VALUES ($1, $2, $3)
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
                insert_query, email, password_hash, False
            )
            user_id = row["id"]

        # Fetch the full user record
        async with database.get_connection() as conn:
            user_row = await conn.fetchrow(select_query, user_id)
            return UserResponse(**dict(user_row))

    @staticmethod
    async def create_user(user: UserCreate) -> Optional[int]:
        password_hash = SecurityService.hash_password(user.password)

        query = """
        INSERT INTO users (first_name, last_name, email, phone_number, role, permissions, password_hash, is_verified)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id;
        """

        # Insert user and get the generated ID
        async with database.get_transaction() as conn:
            row = await conn.fetchrow(
                query,
                user.first_name,
                user.last_name,
                user.email,
                user.phone_number,
                user.role,
                user.permissions,
                password_hash,
                False,
            )

            if row and "id" in row:
                return row["id"]
            return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Union[UserRead, None]:
        query = """
        SELECT *
        FROM users
        WHERE id = $1
        LIMIT 1;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, user_id)
            return UserRead(**dict(row)) if row else None

    @staticmethod
    async def get_user_by_email(email: str) -> Union[UserRead, None]:
        query = """
        SELECT *
        FROM users
        WHERE email = $1
        LIMIT 1;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, email)
            return UserRead(**dict(row)) if row else None

    @staticmethod
    async def get_user_by_pin(password: str) -> Union[UserRead, None]:
        query = """
        SELECT *
        FROM users
        WHERE password_hash = $1
        LIMIT 1;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                SecurityService.hash_password(password),
            )
            return UserRead(**dict(row)) if row else None

    @staticmethod
    async def get_users() -> List[UserRead]:
        query = """SELECT * FROM users;"""

        async with database.get_connection() as conn:
            rows = await conn.fetch(query)

        result = []
        for row in rows:
            result.append(UserRead(**dict(row)))

        return result

    @staticmethod
    async def delete_user(email: str, password: str):
        user = await UserService.validate_user(email, password)

        if not user:
            return False

        delete_query = "DELETE FROM users WHERE id = $1 RETURNING id;"

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(delete_query, user.id)
            return bool(row)

    @staticmethod
    async def delete_user_by_id(id: int) -> bool:
        delete_query = "DELETE FROM users WHERE id = $1 RETURNING id;"

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(delete_query, id)
            return bool(row)

    @staticmethod
    async def update_user(user_id: int, user_update: UserUpdate) -> bool:
        updates = user_update.model_dump(
            exclude_unset=True,
            exclude={"password"},
        )

        if not updates:
            return False

        set_clauses = [
            f"{field} = ${i+1}" for i, field in enumerate(updates.keys())
        ]
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ${len(updates)+1} RETURNING id;"
        values = list(updates.values()) + [user_id]

        async with database.get_transaction() as conn:
            row = await conn.fetchrow(query, *values)
            return bool(row)


class EmailMfaCodeService:
    @staticmethod
    async def create_email_mfa_code(user_id: int, expire_in: timedelta) -> str:
        await EmailMfaCodeService.delete_mfa_codes(user_id)

        code = SecurityService.generate_email_mfa_code()
        expires_at = datetime.now(dt.timezone.utc) + expire_in

        query = """
            INSERT INTO email_mfa_codes (user_id, code_hash, expires_at)
            VALUES ($1, $2, $3);
        """
        async with database.get_transaction() as conn:
            await conn.execute(
                query,
                user_id,
                SecurityService.hash_token(code),
                expires_at,
            )
            return code

    @staticmethod
    async def verify_email_mfa_code(user_id: int, code: str) -> bool:
        verify_query = """
            SELECT code_hash
            FROM email_mfa_codes
            WHERE user_id=$1
            AND code_hash=$2
            AND expires_at > NOW();
        """

        async with database.get_connection() as conn:
            row = await conn.fetchrow(
                verify_query,
                user_id,
                SecurityService.hash_token(code),
            )

        if row:
            async with database.get_transaction() as conn:
                await conn.execute(
                    "DELETE FROM email_mfa_codes WHERE user_id = $1 AND code_hash = $2",
                    user_id,
                    SecurityService.hash_token(code),
                )
            return True

        return False

    @staticmethod
    async def delete_mfa_codes(user_id: int):
        query = "DELETE FROM email_mfa_codes WHERE user_id=$1;"
        async with database.get_transaction() as conn:
            await conn.execute(query, user_id)


class RecoveryCodeService:
    @staticmethod
    async def create_recovery_codes(user_id: int) -> List[str]:
        codes = SecurityService.generate_recovery_codes()

        query = (
            "INSERT INTO recovery_codes (user_id, code_hash) VALUES ($1, $2);"
        )
        async with database.get_transaction() as conn:
            for code in codes:
                await conn.execute(
                    query, user_id, SecurityService.hash_token(code)
                )

        return codes

    @staticmethod
    async def verify_recovery_code(user_id: int, code: str) -> bool:
        query = """
        SELECT code_hash
        FROM recovery_codes
        WHERE user_id = $1 AND code_hash = $2;
        """
        async with database.get_connection() as conn:
            row = await conn.fetchrow(
                query, user_id, SecurityService.hash_token(code)
            )

        if row:
            async with database.get_transaction() as conn:
                await conn.execute(
                    "DELETE FROM recovery_codes WHERE user_id = $1 AND code_hash = $2",
                    user_id,
                    SecurityService.hash_token(code),
                )
            return True

        return False

    @staticmethod
    async def delete_recovery_codes(user_id: int):
        query = "DELETE FROM recovery_codes WHERE user_id = $1;"
        async with database.get_transaction() as conn:
            await conn.execute(query, user_id)

    @staticmethod
    async def regenerate_recovery_codes(user_id: int) -> List[str]:
        await RecoveryCodeService.delete_recovery_codes(user_id)
        return await RecoveryCodeService.create_recovery_codes(user_id)


class TokenService:
    # Refresh tokens
    @staticmethod
    async def create_refresh_token(token: RefreshToken):
        query = """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3);
        """
        async with database.get_transaction() as conn:
            await conn.execute(
                query, token.user_id, token.token_hash, token.expires_at
            )

    @staticmethod
    async def get_refresh_token(token: str) -> RefreshToken | None:
        query = """
        SELECT *
        FROM refresh_tokens
        WHERE token_hash = $1;
        """

        async with database.get_connection() as conn:
            row = await conn.fetchrow(query, SecurityService.hash_token(token))
            return RefreshToken(**dict(row)) if row else None

    @staticmethod
    async def delete_refresh_token(token: str, user_id: int):
        query = """
        DELETE FROM refresh_tokens
        WHERE token_hash = $1 AND user_id = $2;
        """
        async with database.get_transaction() as conn:
            await conn.execute(
                query, SecurityService.hash_token(token), user_id
            )

    @staticmethod
    async def delete_expired_refresh_tokens(user_id: int):
        query = """
        DELETE FROM refresh_tokens
        WHERE user_id = $1 AND expires_at <= NOW();
        """
        async with database.get_transaction() as conn:
            await conn.execute(query, user_id)

    @staticmethod
    async def refresh_token(token: str) -> TokenResponse:
        refresh_token = await TokenService.get_refresh_token(token)

        if not refresh_token or refresh_token.expires_at < dt.datetime.now(
            dt.timezone.utc
        ):
            if refresh_token:
                await TokenService.delete_expired_refresh_tokens(
                    refresh_token.user_id
                )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is expired",
            )

        # You can also rotate the refresh token here if needed
        (access_token, expiry) = SecurityService.generate_jwt(
            refresh_token.user_id,
            timedelta(minutes=settings.access_token_expire_minutes),
            True,
        )

        return TokenResponse(access_token=access_token, expires_at=expiry)

    # Verification tokens
    @staticmethod
    async def create_verification_token(token: VerificationToken):
        query = """
        INSERT INTO verification_tokens (user_id, token_hash, token_type, expires_at)
        VALUES ($1, $2, $3, $4);
        """
        async with database.get_transaction() as conn:
            await conn.execute(
                query,
                token.user_id,
                token.token_hash,
                token.token_type,
                token.expires_at,
            )

    @staticmethod
    async def delete_verification_token(user_id: int):
        query = """
        DELETE FROM verification_tokens
        WHERE user_id = $1;
        """
        async with database.get_transaction() as conn:
            await conn.execute(query, user_id)

    @staticmethod
    async def delete_expired_verification_tokens():
        query = """
        DELETE FROM verification_tokens
        WHERE expires_at <= NOW();
        """
        async with database.get_transaction() as conn:
            await conn.execute(query)

    @staticmethod
    async def get_verification_token(
        token: str, type: str
    ) -> VerificationToken | None:
        query = """
        SELECT *
        FROM verification_tokens
        WHERE token_hash = $1
          AND token_type = $2;
        """

        async with database.get_connection() as conn:
            row = await conn.fetchrow(
                query, SecurityService.hash_token(token), type
            )
            return VerificationToken(**dict(row)) if row else None
