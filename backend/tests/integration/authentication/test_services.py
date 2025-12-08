# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
import time
import unittest
from fastapi import HTTPException
from app.authentication.schemas import (
    RefreshToken,
    RegisterRequest,
    UserCreate,
    UserUpdate,
    VerificationToken,
)
from app.authentication.utils import SecurityService
from app.database import database
from app.authentication.services import (
    EmailMfaCodeService,
    RecoveryCodeService,
    UserService,
    TokenService,
)
import datetime as dt
from datetime import datetime, timedelta


email = "test@gmail.com"
password = "test_password"
user_create = RegisterRequest(email=email, password=password)


class TestUserService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_register_user(self):
        await UserService.register_user(email, password)

        user1 = await UserService.get_user_by_email(email)
        assert user1
        self.assertEqual(user1.email, email)

        resp = await UserService.check_user_exists(email)
        self.assertTrue(resp)

        # Clean-up
        await UserService.delete_user(email, password)
        resp = await UserService.check_user_exists(email)
        self.assertFalse(resp)

    async def test_create_user(self):
        user = UserCreate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone_number="+14165550123",
            password="StrongPassw0rd!",
            authenticator_mfa_enabled=False,
            mfa_secret="",
            is_verified=False,
            role="standard",
            permissions=["", "write", "delete"],
            province="Ontario",
            location_permissions=["All"],
        )
        await UserService.create_user(user)

        user1 = await UserService.get_user_by_email(user.email)
        assert user1
        self.assertEqual(user1.email, user.email)

        resp = await UserService.check_user_exists(user.email)
        self.assertTrue(resp)

        # Clean-up
        await UserService.delete_user(user.email, user.password)
        resp = await UserService.check_user_exists(user.email)
        self.assertFalse(resp)

    async def test_update_user(self):
        await UserService.register_user(email, password)

        user = await UserService.get_user_by_email(email)
        assert user
        self.assertEqual(user.email, email)

        new_email = "test2@gmail.com"
        last_login = dt.datetime.now(dt.timezone.utc)
        update_user = UserUpdate()
        update_user.email = new_email
        update_user.last_login = last_login
        update_user.authenticator_mfa_enabled = True

        await UserService.update_user(user.id, update_user)

        # Check
        user = await UserService.get_user_by_email(new_email)

        assert user
        self.assertEqual(user.email, new_email)
        self.assertEqual(user.authenticator_mfa_enabled, True)
        self.assertIsNotNone(user.last_login)

        # Clean-up
        await UserService.delete_user(new_email, password)

    async def test_get_user(self):
        user = await UserService.register_user(email, password)

        # Email
        user1 = await UserService.get_user_by_email(email)
        assert user1
        self.assertEqual(user1.email, email)

        # ID
        user2 = await UserService.get_user_by_id(user.id)
        assert user2
        self.assertEqual(user2.email, email)

        # Clean-up
        await UserService.delete_user(email, password)

    async def test_check_user_exists(self):
        await UserService.register_user(email, password)

        resp = await UserService.check_user_exists(email)
        self.assertTrue(resp)

        # Clean-up
        await UserService.delete_user(email, password)

    async def test_validate_user(self):
        await UserService.register_user(email, password)

        resp = await UserService.validate_user(email, password)
        self.assertTrue(resp)

        # Clean-up
        await UserService.delete_user(email, password)


email = "test38@gmail.com"
password = "test_password"


class TestEmailMfaCodes(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        self.user = await UserService.register_user(email, password)

    async def asyncTearDown(self) -> None:
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_mfa_codes(self):
        code = await EmailMfaCodeService.create_email_mfa_code(
            self.user.id, timedelta(minutes=5)
        )

        self.assertTrue(len(code) == 6)

    async def test_verify_mfa_codes(self):
        code = await EmailMfaCodeService.create_email_mfa_code(
            self.user.id, timedelta(minutes=5)
        )

        # Test
        result = await EmailMfaCodeService.verify_email_mfa_code(
            self.user.id, code
        )
        self.assertTrue(result)

        check_deleted = await EmailMfaCodeService.verify_email_mfa_code(
            self.user.id, code
        )
        self.assertFalse(check_deleted)

    async def test_expired_mfa_codes(self):
        code = await EmailMfaCodeService.create_email_mfa_code(
            self.user.id, timedelta(minutes=-5)
        )

        # Test
        result = await EmailMfaCodeService.verify_email_mfa_code(
            self.user.id, code
        )
        self.assertFalse(result)


email = "test33@gmail.com"
password = "test_password"


class TestRecoveryCodeService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        self.user = await UserService.register_user(email, password)

    async def asyncTearDown(self) -> None:
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_recovery_codes(self):
        codes = await RecoveryCodeService.create_recovery_codes(self.user.id)

        self.assertTrue(len(codes) == 10)

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_verify_recovery_code_true(self):
        codes = await RecoveryCodeService.create_recovery_codes(self.user.id)

        self.assertTrue(len(codes) == 10)

        result = await RecoveryCodeService.verify_recovery_code(
            self.user.id,
            codes[0],
        )
        self.assertTrue(result)

        result = await RecoveryCodeService.verify_recovery_code(
            self.user.id,
            codes[0],
        )
        self.assertFalse(result)

    async def test_verify_recovery_false(self):

        _ = await RecoveryCodeService.create_recovery_codes(self.user.id)
        result = await RecoveryCodeService.verify_recovery_code(
            self.user.id,
            "invalid",
        )
        self.assertFalse(result)

    async def test_regenerate_codes(self):
        codes = await RecoveryCodeService.create_recovery_codes(self.user.id)

        for c in codes:
            self.assertTrue(
                await RecoveryCodeService.verify_recovery_code(self.user.id, c)
            )

        new_codes = await RecoveryCodeService.regenerate_recovery_codes(
            self.user.id
        )

        for c in codes:
            self.assertFalse(
                await RecoveryCodeService.verify_recovery_code(self.user.id, c)
            )

        for c in new_codes:
            self.assertTrue(
                await RecoveryCodeService.verify_recovery_code(self.user.id, c)
            )


token = "token"
refresh_token = RefreshToken(
    id=0,
    user_id=1,
    token_hash=SecurityService.hash_token(token),
    expires_at=datetime.now(dt.timezone.utc),
    created_at=None,
)

email = "test3@gmail.com"
password = "test_password"


class TestRefreshTokenService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        self.user = await UserService.register_user(email, password)

    async def asyncTearDown(self) -> None:
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_refresh_token(self):
        refresh_token.user_id = self.user.id

        await TokenService.create_refresh_token(refresh_token)

        got_token = await TokenService.get_refresh_token(token)
        assert got_token

        self.assertEqual(got_token.token_hash, refresh_token.token_hash)
        self.assertEqual(got_token.user_id, self.user.id)

    async def test_get_refresh_token(self):
        refresh_token.user_id = self.user.id

        await TokenService.create_refresh_token(refresh_token)

        got_token = await TokenService.get_refresh_token(token)
        assert got_token

        self.assertEqual(got_token.token_hash, refresh_token.token_hash)
        self.assertEqual(got_token.user_id, self.user.id)

    async def test_delete_expired_refresh_token(self):
        refresh_token.user_id = self.user.id
        refresh_token.expires_at = datetime.now(dt.timezone.utc) - timedelta(
            days=1
        )
        await TokenService.create_refresh_token(refresh_token)

        got_token = await TokenService.get_refresh_token(token)
        self.assertEqual(got_token.token_hash, refresh_token.token_hash)

        time.sleep(5)

        await TokenService.delete_expired_refresh_tokens(self.user.id)
        got_token = await TokenService.get_refresh_token(token)
        self.assertIsNone(got_token)

    async def test_delete_refresh_token(self):
        refresh_token.user_id = self.user.id
        refresh_token.expires_at = datetime.now(dt.timezone.utc) - timedelta(
            days=1
        )
        await TokenService.create_refresh_token(refresh_token)

        got_token = await TokenService.get_refresh_token(token)
        self.assertEqual(got_token.token_hash, refresh_token.token_hash)

        time.sleep(5)

        await TokenService.delete_refresh_token(token, self.user.id)
        got_token = await TokenService.get_refresh_token(token)
        self.assertIsNone(got_token)

    async def test_refresh_token_valid(self):
        refresh_token.user_id = self.user.id
        refresh_token.expires_at = datetime.now(dt.timezone.utc) + timedelta(
            days=1
        )

        await TokenService.create_refresh_token(refresh_token)

        # Test
        token_response = await TokenService.refresh_token(token)
        self.assertIsNotNone(token_response.access_token)

    async def test_refresh_token_expired(self):
        refresh_token.user_id = self.user.id
        refresh_token.expires_at = datetime.now(dt.timezone.utc) - timedelta(
            days=1
        )
        await TokenService.create_refresh_token(refresh_token)

        # Test
        with self.assertRaises(HTTPException) as e:
            await TokenService.refresh_token(token)

        self.assertEqual(e.exception.status_code, 401)
        self.assertIn("Refresh token is expired", str(e.exception.detail))


token = "token"
v_token = VerificationToken(
    id=0,
    user_id=1,
    token_hash=SecurityService.hash_token(token),
    token_type="email_verification",
    expires_at=datetime.now(dt.timezone.utc),
    created_at=None,
)

email = "test7@gmail.com"
password = "test_password"


class TestVerificationTokenService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        self.user = await UserService.register_user(email, password)

    async def asyncTearDown(self) -> None:
        await UserService.delete_user(email, password)
        await database.disconnect()

    async def test_create_verification_token(self):
        v_token.user_id = self.user.id

        await TokenService.create_verification_token(v_token)

        got_token = await TokenService.get_verification_token(
            token, v_token.token_type
        )
        assert got_token

        self.assertEqual(got_token.token_hash, v_token.token_hash)
        self.assertEqual(got_token.user_id, self.user.id)

    async def test_get_verification_token(self):
        v_token.user_id = self.user.id

        await TokenService.create_verification_token(v_token)

        got_token = await TokenService.get_verification_token(
            token, v_token.token_type
        )
        assert got_token

        self.assertEqual(got_token.token_hash, v_token.token_hash)
        self.assertEqual(got_token.user_id, self.user.id)

    async def test_delete_expired_verification_token(self):
        v_token.user_id = self.user.id
        v_token.expires_at = datetime.now(dt.timezone.utc) - timedelta(days=1)
        await TokenService.create_verification_token(v_token)

        got_token = await TokenService.get_verification_token(
            token, v_token.token_type
        )
        self.assertEqual(got_token.token_hash, v_token.token_hash)

        time.sleep(5)

        await TokenService.delete_verification_token(self.user.id)
        got_token = await TokenService.get_refresh_token(token)
        self.assertIsNone(got_token)

    async def test_delete_verification_token(self):
        v_token.user_id = self.user.id
        v_token.expires_at = datetime.now(dt.timezone.utc) - timedelta(days=1)
        await TokenService.create_verification_token(v_token)

        got_token = await TokenService.get_verification_token(
            token, v_token.token_type
        )
        self.assertEqual(got_token.token_hash, v_token.token_hash)

        time.sleep(5)

        await TokenService.delete_verification_token(self.user.id)
        got_token = await TokenService.get_refresh_token(token)
        self.assertIsNone(got_token)
