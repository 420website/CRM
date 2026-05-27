# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
import pyotp
import datetime as dt
from starlette.types import Scope

from app.core.authentication.schemas import (
    Email,
    ForgotPassword,
    LoginRequest,
    RegisterRequest,
    ResetPassword,
    MFAVerifiactionCode,
    UserCreate,
    UserUpdate,
)
from app.common.crypt import SecurityService
from app.common.storage.postgres import database
from app.core.authentication.services import (
    RecoveryCodeService,
    TokenService,
    UserService,
)
from datetime import datetime
from app.common.config import settings
from app.common.dependencies import get_current_user, get_user_pending_mfa
from app.core.authentication.router import (
    create_user,
    delete_user,
    disable_authenticator_mfa,
    get_user_permissions,
    get_users,
    login,
    logout,
    refresh_token,
    regenerate_recovery_codes,
    register,
    send_email_mfa_code,
    send_verification_email,
    setup_authenticator_mfa,
    update_users,
    verify_authenticator_mfa,
    verify_email,
    forgot_password,
    reset_password,
    verify_email_mfa,
    verify_recovery_code,
)
from app.testing.router import register_user

email = "test4@example.com"
password = "securepassword123"
base_url = "http://localhost:8001"

user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)

mfa_req = "123456"


@patch("app.core.authentication.services.EmailService", new_callable=MagicMock)
async def mock_send_verification_email(mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    # We'll extract the token from here
    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg
        # Look for the verification URL in the HTML
        import re

        match = re.search(r'token=([^"&]+)', html_content)
        if match:
            captured_token["token"] = match.group(1)
        return mock_email_service

    mock_email_service.body.side_effect = mock_body
    mock_email_service.send.return_value = None

    # This makes EmailService() return our mock instance
    mock_email_service_class.return_value = mock_email_service

    await send_verification_email(Email(email=email))
    return captured_token["token"]


@patch("app.core.authentication.services.EmailService", new_callable=MagicMock)
async def mock_forgot_password(mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    # We'll extract the token from here
    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg
        # Look for the verification URL in the HTML
        import re

        match = re.search(r'token=([^"&]+)', html_content)
        if match:
            captured_token["token"] = match.group(1)
        return mock_email_service

    mock_email_service.body.side_effect = mock_body
    mock_email_service.send.return_value = None

    # This makes EmailService() return our mock instance
    mock_email_service_class.return_value = mock_email_service

    await forgot_password(ForgotPassword(email=email))
    return captured_token["token"]


@patch("app.core.authentication.services.EmailService", new_callable=MagicMock)
async def mock_mfa_email(user, mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    # We'll extract the token from here
    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg
        # Look for the verification URL in the HTML
        import re

        match = re.search(
            r'<div class="verification-code"[^>]*>([^<]+)</div>', html_content
        )
        if match:
            captured_token["code"] = match.group(1).strip()
        return mock_email_service

    mock_email_service.body.side_effect = mock_body
    mock_email_service.send.return_value = None

    # This makes EmailService() return our mock instance
    mock_email_service_class.return_value = mock_email_service

    await send_email_mfa_code(user)
    return captured_token["code"]


@patch("app.core.authentication.services.EmailService", new_callable=MagicMock)
async def mock_register(mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    # We'll extract the token from here
    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg
        # Look for the verification URL in the HTML
        import re

        match = re.search(r'token=([^"&]+)', html_content)
        if match:
            captured_token["token"] = match.group(1)
        return mock_email_service

    mock_email_service.body.side_effect = mock_body
    mock_email_service.send.return_value = None

    # This makes EmailService() return our mock instance
    mock_email_service_class.return_value = mock_email_service

    await register(user_create)
    return captured_token["token"]


async def get_validated_user():
    # token = await mock_register()
    # await verify_email(token)
    await register_user(user_create)
    response = await login(login_request)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=response.access_token,
    )

    user = await get_user_pending_mfa(credentials=credentials)
    response = await setup_authenticator_mfa(user)
    totp = pyotp.TOTP(response.secret)
    code = totp.now()

    user = await get_user_pending_mfa(credentials=credentials)
    response = Response()
    result = await verify_authenticator_mfa(
        MFAVerifiactionCode(code=code), response, user
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=result.access_token,
    )

    user = await get_current_user(credentials=credentials)
    return user


class TestAuthRouter(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)
        await database.connect()
        await UserService.delete_user(email, password)

    async def asyncTearDown(self) -> None:
        await UserService.delete_user(email, password)
        await database.disconnect()

    # register
    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_register_success(self, _):
        await register(user_create)
        response = await UserService.get_user_by_email(email)

        now = datetime.now(dt.timezone.utc)

        self.assertEqual(response.email, email)
        self.assertEqual(response.authenticator_mfa_enabled, False)
        self.assertEqual(response.last_login, None)
        self.assertEqual(now.date(), response.created_at.date())
        self.assertEqual(now.hour, response.created_at.hour)
        self.assertEqual(now.minute, response.created_at.minute)

        await UserService.delete_user(email, password)

    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_register_duplicate(self, _):
        await register(user_create)
        response = await UserService.get_user_by_email(email)
        self.assertEqual(response.email, user_create.email)

        # Register again, expect duplication error
        with self.assertRaises(HTTPException) as cm:
            await register(user_create)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn(
            "email already registered", str(cm.exception.detail).lower()
        )

        # Cleanup
        await UserService.delete_user(email, password)

    # send verification email
    async def test_send_verification_email(self):
        original_token = await mock_register()

        token = await mock_send_verification_email()
        self.assertNotEqual(original_token, token)

        response = await verify_email(token)
        self.assertEqual(response["message"], "Email verified successfully")

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_send_verification_email_unregistered(self):
        with self.assertRaises(HTTPException) as cm:
            await mock_send_verification_email()

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("Invalid email.", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # verify email
    async def test_verify_email(self):
        token = await mock_register()

        response = await verify_email(token)
        self.assertEqual(response["message"], "Email verified successfully")

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_verify_email_unsuccessful(self):
        await mock_register()

        with self.assertRaises(HTTPException) as cm:
            await verify_email("invalid")

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid or expired token", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # login
    async def test_login_success(self):
        token = await mock_register()
        await verify_email(token)

        # test
        response = await login(login_request)

        payload = jwt.decode(
            response.access_token,
            settings.jwt_access_secret,
            algorithms=settings.jwt_algorithm,
        )

        self.assertEqual(response.authenticator_mfa_setup, False)
        self.assertEqual(response.mfa_required, True)
        self.assertEqual(payload["auth"], False)

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_login_no_user(self):
        with self.assertRaises(HTTPException) as cm:
            await login(login_request)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid email or password", str(cm.exception.detail).lower()
        )

    async def test_login_unverified(self):
        await mock_register()
        with self.assertRaises(HTTPException) as cm:
            await login(login_request)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn(
            "Please verify your email first", str(cm.exception.detail)
        )

        # Cleanup
        await UserService.delete_user(email, password)

    # forgot password
    async def test_forgot_pasword_successful(self):
        token = await mock_register()
        await verify_email(token)

        response = await mock_forgot_password()
        self.assertIsNotNone(response)

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_forgot_password_no_user(self):
        token = await mock_register()
        await verify_email(token)

        response = await forgot_password(
            ForgotPassword(email="other@gmail.com")
        )

        self.assertEqual(
            response["message"], "If email exists, reset link sent"
        )

        # Cleanup
        await UserService.delete_user(email, password)

    # reset password
    async def test_reset_password_successful(self):
        token = await mock_register()
        await verify_email(token)

        reset_token = await mock_forgot_password()
        new_password = "newpassword"
        response = await reset_password(
            ResetPassword(token=reset_token, new_password=new_password)
        )

        # test
        self.assertEqual(response["message"], "Password updated successfully")

        # Cleanup
        await UserService.delete_user(email, new_password)

    async def test_reset_password_no_user(self):
        token = await mock_register()
        await verify_email(token)
        await mock_forgot_password()
        new_password = "newpassword"

        with self.assertRaises(HTTPException) as cm:
            await reset_password(
                ResetPassword(token="invalid", new_password=new_password)
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid or expired token", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # setup authenticator mfa
    async def test_setup_authenticator_mfa_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)

        # Test
        response = await setup_authenticator_mfa(user)
        self.assertIsNotNone(response.secret)
        self.assertIsNotNone(response.qr_code)

        updated_user = await UserService.get_user_by_email(email)
        self.assertEqual(
            response.secret,
            SecurityService.decrypt_mfa_secret(updated_user.mfa_secret),
        )

        # Cleanup
        await UserService.delete_user(email, password)

    # verify authenticator  mfa
    async def test_verify_authenticator_mfa_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(response.secret)
        code = totp.now()

        # Test
        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        result = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        self.assertIsNotNone(result.access_token)
        self.assertIsNotNone(result.expires_at)
        self.assertIsNotNone(result.recovery_codes)
        self.assertEqual(result.token_type, "bearer")

        # Refresh token
        set_cookie_header = response.headers.get("set-cookie")
        if "refresh_token=" in set_cookie_header:
            token_part = set_cookie_header.split("refresh_token=")[1]
            actual_token = token_part.split(";")[0]

            token = await TokenService.get_refresh_token(actual_token)
            self.assertEqual(
                token.token_hash,
                SecurityService.hash_token(actual_token),
            )

        # User
        user = await UserService.get_user_by_email(email)
        self.assertTrue(user.authenticator_mfa_enabled)

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_verify_authenticator_mfa_before_setup(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        # Test
        with self.assertRaises(HTTPException) as cm:
            await verify_authenticator_mfa(mfa_req, response, user)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("MFA not set up", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # send mfa code email
    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_send_mfa_email(self, _):
        await mock_register()
        token = await mock_send_verification_email()
        await verify_email(token)

        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )
        user = await get_user_pending_mfa(credentials=credentials)

        result = await send_email_mfa_code(user)
        self.assertEqual(
            result["message"],
            "MFA code sent successful. Check your email to verify.",
        )

        # Cleanup
        await UserService.delete_user(email, password)

    # verify  email  mfa
    async def test_verify_email_mfa_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        code = await mock_mfa_email(user)

        # Test
        response = Response()
        result = await verify_email_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        self.assertIsNotNone(result.access_token)
        self.assertIsNotNone(result.expires_at)
        self.assertIsNone(result.recovery_codes)
        self.assertEqual(result.token_type, "bearer")

        # Refresh token
        set_cookie_header = response.headers.get("set-cookie")
        if "refresh_token=" in set_cookie_header:
            token_part = set_cookie_header.split("refresh_token=")[1]
            actual_token = token_part.split(";")[0]

            token = await TokenService.get_refresh_token(actual_token)
            self.assertEqual(
                token.token_hash,
                SecurityService.hash_token(actual_token),
            )

        # User
        user = await UserService.get_user_by_email(email)
        self.assertFalse(user.authenticator_mfa_enabled)

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_verify_email_invalid(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)

        # Test
        with self.assertRaises(HTTPException) as cm:
            await verify_email_mfa(
                MFAVerifiactionCode(code="123456"), Response(), user
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid MFA code", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # recovery codes
    async def test_recovery_codes_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        setup_response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(setup_response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        verify_response = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        if not verify_response.recovery_codes:
            raise Exception("Should be recovery codes. ")

        # Test
        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()

        _ = await verify_recovery_code(
            MFAVerifiactionCode(code=verify_response.recovery_codes[0]),
            response,
            user,
        )

        # Refresh token
        set_cookie_header = response.headers.get("set-cookie")
        if "refresh_token=" in set_cookie_header:
            token_part = set_cookie_header.split("refresh_token=")[1]
            actual_token = token_part.split(";")[0]

            token = await TokenService.get_refresh_token(actual_token)
            self.assertEqual(
                token.token_hash,
                SecurityService.hash_token(actual_token),
            )

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_recovery_codes_before_setup(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        # Test
        response = Response()
        user = await get_user_pending_mfa(credentials=credentials)

        with self.assertRaises(HTTPException) as cm:
            await verify_recovery_code(
                MFAVerifiactionCode(code="12345678"), response, user
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("MFA not set up", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # Regenerate recovery codes
    async def test_regenerate_recovery_codes_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        setup_response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(setup_response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        result = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        if not result.recovery_codes:
            raise Exception("Should be recovery codes. ")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=result.access_token,
        )

        user = await get_current_user(credentials=credentials)

        # Test
        for c in result.recovery_codes:
            self.assertTrue(
                await RecoveryCodeService.verify_recovery_code(user.id, c)
            )

        new_codes = await regenerate_recovery_codes(user)

        for c in result.recovery_codes:
            self.assertFalse(
                await RecoveryCodeService.verify_recovery_code(user.id, c)
            )

        for c in new_codes.codes:
            self.assertTrue(
                await RecoveryCodeService.verify_recovery_code(user.id, c)
            )

        # Cleanup
        await UserService.delete_user(email, password)

    async def test_regenerate_recovery_codes_unsuccess(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        setup_response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(setup_response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        result = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=result.access_token,
        )

        user = await get_current_user(credentials=credentials)
        user.authenticator_mfa_enabled = False

        # Test
        with self.assertRaises(HTTPException) as cm:
            await regenerate_recovery_codes(user)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("MFA not set up", str(cm.exception.detail))

        # Cleanup
        await UserService.delete_user(email, password)

    # disable mfa
    async def test_disable_authenticator_mfa_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        result = await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )
        user = await UserService.get_user_by_email(email)

        # Test
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=result.access_token,
        )

        user = await get_current_user(credentials=credentials)
        response = await disable_authenticator_mfa(
            MFAVerifiactionCode(code=code), user
        )
        user = await get_current_user(credentials=credentials)
        self.assertFalse(user.authenticator_mfa_enabled)
        self.assertIsNone(user.mfa_secret)

        # Cleanup
        await UserService.delete_user(email, password)

    # refresh token
    async def test_refresh_tokens_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        # Refresh token
        set_cookie_header = response.headers.get("set-cookie")
        assert "refresh_token=" in set_cookie_header

        token_part = set_cookie_header.split("refresh_token=")[1]
        actual_token = token_part.split(";")[0]

        # Test
        cookie_header = f"refresh_token={actual_token}".encode()

        scope: Scope = {
            "type": "http",
            "method": "POST",
            "path": "/auth/refresh",
            "headers": [(b"cookie", cookie_header)],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "scheme": "http",
        }

        request = Request(scope)
        result = await refresh_token(request)

        self.assertIsNotNone(result.access_token)
        self.assertIsNotNone(result.expires_at)
        self.assertEqual(result.token_type, "bearer")

        # Cleanup
        await UserService.delete_user(email, password)

    # logout
    async def test_logout_success(self):
        token = await mock_register()
        await verify_email(token)
        response = await login(login_request)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=response.access_token,
        )

        user = await get_user_pending_mfa(credentials=credentials)
        response = await setup_authenticator_mfa(user)
        totp = pyotp.TOTP(response.secret)
        code = totp.now()

        user = await get_user_pending_mfa(credentials=credentials)
        response = Response()
        await verify_authenticator_mfa(
            MFAVerifiactionCode(code=code), response, user
        )

        # Refresh token
        set_cookie_header = response.headers.get("set-cookie")
        assert "refresh_token=" in set_cookie_header

        token_part = set_cookie_header.split("refresh_token=")[1]
        actual_token = token_part.split(";")[0]

        # Test
        cookie_header = f"refresh_token={actual_token}".encode()

        scope: Scope = {
            "type": "http",
            "method": "POST",
            "path": "/auth/refresh",
            "headers": [(b"cookie", cookie_header)],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
            "scheme": "http",
        }

        request = Request(scope)
        results = await TokenService.get_refresh_token(actual_token)
        self.assertIsNotNone(results)

        response = Response()
        result = await logout(response, request)
        self.assertEqual(result["message"], "Successfully logged out.")

        cookie_header = response.headers.get("set-cookie")
        self.assertIsNotNone(cookie_header)
        self.assertIn("refresh_token=", cookie_header)

        results = await TokenService.get_refresh_token(actual_token)
        self.assertIsNone(results)

        # Cleanup
        await UserService.delete_user(email, password)

    # CRUD
    async def test_get_users_success(self):
        user = await get_validated_user()
        response = await get_users(user)

        self.assertGreaterEqual(len(response), 1)

        await UserService.delete_user(email, password)

    async def test_get_user_permissions_success(self):
        user = await get_validated_user()
        response = await get_user_permissions(user)

        # validate
        self.assertEqual(response.user_role, "admin")
        self.assertEqual(response.user_permissions, [])
        self.assertEqual(response.province, "Ontario")
        self.assertEqual(response.location_permissions, ["All"])

        await UserService.delete_user(email, password)

    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_create_users_success(self, _):
        user = await get_validated_user()
        response1 = await get_users(user)

        new_user = UserCreate(
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

        await create_user(new_user, user)
        response2 = await get_users(user)

        self.assertTrue(len(response2) > len(response1))

        await UserService.delete_user(new_user.email, new_user.password)

    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_update_users_success(self, _):
        user = await get_validated_user()

        new_user = UserCreate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson2@example.com",
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

        await create_user(new_user, user)
        response = await get_users(user)
        id = [r.id for r in response if r.first_name == "Alice"][0]

        update_user = UserUpdate()
        update_user.first_name = "Tom"

        response = await update_users(id, update_user, user)
        users = await get_users(user)

        id = [r.id for r in users if r.first_name == "Tom"][0]
        self.assertIsNotNone(id)

        await UserService.delete_user(new_user.email, new_user.password)

    @patch(
        "app.core.authentication.services.EmailService.send",
        new_callable=MagicMock,
    )
    async def test_delete_users_success(self, _):
        user = await get_validated_user()

        new_user = UserCreate(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson22@example.com",
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

        await create_user(new_user, user)
        response = await get_users(user)
        id = [r.id for r in response if r.first_name == "Alice"][0]

        response = await delete_user(id, user)
        self.assertEqual(response["message"], "Successfully deleted user.")

        await UserService.delete_user(new_user.email, new_user.password)
