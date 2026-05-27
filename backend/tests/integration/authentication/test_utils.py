# tests/auth/test_utils.py
# pyright: reportOptionalMemberAccess=none, reportArgumentType=none
import asyncio
import unittest
from jose import jwt
from app.common.config import settings
from app.common.storage.postgres import database
from app.common.crypt import SecurityService
from datetime import datetime, timedelta
import datetime as dt

password = "test_password"


class TestSercurityService(unittest.TestCase):
    async def asyncSetUp(self) -> None:
        await database.connect()
        asyncio.get_event_loop().set_debug(False)

    async def asyncTearDown(self) -> None:
        await database.disconnect()

    def test_hash_password(self):
        hash = SecurityService.hash_password(password)

        check = SecurityService.verify_password(password, hash)
        self.assertTrue(check)

    def test_encrypt_decrypt_mfa_secret(self):
        secret = SecurityService.generate_mfa_secret()

        encrypted = SecurityService.encrypt_mfa_secret(secret)
        decrypted = SecurityService.decrypt_mfa_secret(encrypted)

        self.assertEqual(secret, decrypted)

    def test_generate_qr_code(self):
        pass

    def test_verify_totop(self):
        pass

    def test_generate_temp_token(self):
        expires_delta = timedelta(30)
        token, _ = SecurityService.generate_jwt(1, expires_delta, False)

        payload = jwt.decode(
            token,
            settings.jwt_access_secret,
            algorithms=settings.jwt_algorithm,
        )

        self.assertEqual(payload.get("sub"), "1")
        self.assertEqual(payload.get("auth"), False)

    def test_generate_access_token(self):
        expires_delta = timedelta(30)
        token, _ = SecurityService.generate_jwt(1, expires_delta, True)

        payload = jwt.decode(
            token,
            settings.jwt_access_secret,
            algorithms=settings.jwt_algorithm,
        )

        expected_exp = datetime.now(dt.timezone.utc) + expires_delta
        actual_exp = dt.datetime.fromtimestamp(
            payload.get("exp")  # pyright: ignore[reportArgumentType]
        )

        self.assertEqual(payload.get("sub"), "1")
        self.assertEqual(payload.get("auth"), True)
        self.assertEqual(actual_exp.date(), expected_exp.date())
        self.assertEqual(actual_exp.hour, expected_exp.hour)
        self.assertEqual(actual_exp.minute, expected_exp.minute)

    def test_decode_access_token(self):
        expires_delta = timedelta(30)
        token, _ = SecurityService.generate_jwt(1, expires_delta, True)
        payload = SecurityService.decode_jwt(token)
        assert payload

        expected_exp = datetime.now(dt.timezone.utc) + expires_delta
        actual_exp = dt.datetime.fromtimestamp(
            payload.get("exp")  # pyright: ignore[reportArgumentType]
        )

        self.assertEqual(payload.get("sub"), 1)
        self.assertEqual(payload.get("auth"), True)
        self.assertEqual(actual_exp.date(), expected_exp.date())
        self.assertEqual(actual_exp.hour, expected_exp.hour)
        self.assertEqual(actual_exp.minute, expected_exp.minute)

    def test_generate_refresh_token(self):
        token = SecurityService.generate_secure_token()
        hash = SecurityService.hash_token(token)

        check = SecurityService.verify_secure_token(token, hash)
        self.assertTrue(check)

    def test_generate_recovery_codes(self):
        codes = SecurityService.generate_recovery_codes()

        self.assertTrue(len(codes) == 10)
        for c in codes:
            self.assertTrue(len(c) == 8)
