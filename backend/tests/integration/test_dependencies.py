# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
from datetime import timedelta
import unittest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.authentication.services import UserService
from app.common.crypt import SecurityService
from app.common.dependencies import get_current_user, get_user_pending_mfa
from app.core.authentication.schemas import RegisterRequest
from app.common.storage.postgres import database

email = "test5@example.com"
password = "securepassword123"
user_create = RegisterRequest(email=email, password=password)


class TestGetCurrentUser(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_get_current_user_success(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(30), True
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        user = await get_current_user(credentials=credentials)
        self.assertEqual(user.id, response.id)
        self.assertEqual(user.email, email)

        # cleanup
        await UserService.delete_user(email, password)

    async def test_get_current_user_no_token(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=""
        )
        with self.assertRaises(HTTPException) as cm:
            await get_current_user(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid authentication credentials",
            str(cm.exception.detail).lower(),
        )

    async def test_get_current_user_no_user(self):
        token, _ = SecurityService.generate_jwt(-1, timedelta(30), True)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        with self.assertRaises(HTTPException) as cm:
            await get_current_user(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "user not found",
            str(cm.exception.detail).lower(),
        )

    async def test_get_current_user_temp_token(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(5), False
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        with self.assertRaises(HTTPException) as cm:
            await get_current_user(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid authentication credentials",
            str(cm.exception.detail).lower(),
        )

        # cleanup
        await UserService.delete_user(email, password)

    async def test_get_current_expired_token(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(-30), True
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        with self.assertRaises(HTTPException) as cm:
            await get_current_user(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid authentication credentials",
            str(cm.exception.detail).lower(),
        )

        # cleanup
        await UserService.delete_user(email, password)


class TestGetCurrentUserPendingMfA(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    async def test_get_user_pending_mfa_success(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(5), False
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        user = await get_user_pending_mfa(credentials=credentials)
        self.assertEqual(user.id, response.id)
        self.assertEqual(user.email, email)

        # cleanup
        await UserService.delete_user(email, password)

    async def test_get_user_pending_mfa_already_enabled(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(30), True
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )

        with self.assertRaises(HTTPException) as cm:
            await get_user_pending_mfa(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "This endpoint is for users who have not completed MFA",
            str(cm.exception.detail),
        )

        # cleanup
        await UserService.delete_user(email, password)

    async def test_get_user_pending_mfa_no_user(self):
        token, _ = SecurityService.generate_jwt(-1, timedelta(5), False)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        with self.assertRaises(HTTPException) as cm:
            await get_user_pending_mfa(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "user not found",
            str(cm.exception.detail).lower(),
        )

    async def test_get_user_pending_mfa_no_token(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=""
        )
        with self.assertRaises(HTTPException) as cm:
            await get_user_pending_mfa(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid authentication credentials",
            str(cm.exception.detail).lower(),
        )

    async def test_get_user_pending_mfa_expired_token(self):
        response = await UserService.register_user(email, password)

        token, _ = SecurityService.generate_jwt(
            response.id, timedelta(-30), True
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        )
        with self.assertRaises(HTTPException) as cm:
            await get_user_pending_mfa(credentials=credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn(
            "invalid authentication credentials",
            str(cm.exception.detail).lower(),
        )

        # cleanup
        await UserService.delete_user(email, password)
