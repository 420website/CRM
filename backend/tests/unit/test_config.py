import unittest
from unittest.mock import patch
from app.config import Settings, get_env


class TestSettings(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "JWT_ACCESS_SECRET": "access_secret",
            "JWT_REFRESH_SECRET": "refresh_secret",
            "JWT_ALGORITHM": "HS256",
            "MFA_ENCRYPTION_KEY": "mfa_key",
            "DATABASE_URL": "sqlite:///test.db",
            "MYSQL_HOST": "localhost",
            "MYSQL_USER": "user",
            "MYSQL_PASSWORD": "pass",
            "MYSQL_DATABASE": "test_db",
            "ALLOWED_ORIGINS": "http://localhost,http://example.com",
            "SUPPORT_EMAIL": "test@example.com",
            "SUPPORT_EMAIL_PASSWORD": "email_pass",
            "APP_NAME": "test name",
            "DEBUG": "True",
        },
        clear=True,
    )
    # def test_settings_load(self):
    #     settings = Settings()
    #
    #     self.assertEqual(settings.jwt_access_secret, "access_secret")
    #     self.assertEqual(settings.jwt_refresh_secret, "refresh_secret")
    #     self.assertEqual(settings.jwt_algorithm, "HS256")
    #     self.assertEqual(settings.mfa_secret_key, "mfa_key")
    #     self.assertEqual(settings.database_url, "sqlite:///test.db")
    #     self.assertEqual(settings.host, "localhost")
    #     self.assertEqual(settings.user, "user")
    #     self.assertEqual(settings.password, "pass")
    #     self.assertEqual(settings.db, "test_db")
    #     self.assertEqual(
    #         settings.allowed_origins, "http://localhost,http://example.com"
    #     )
    #     self.assertEqual(settings.email, "test@example.com")
    #     self.assertEqual(settings.email_pw, "email_pass")
    #     self.assertTrue(settings.debug)
    #     self.assertEqual(settings.access_token_expire_minutes, 30)
    #     self.assertEqual(settings.refresh_token_expire_days, 7)

    @patch.dict("os.environ", {}, clear=True)
    def test_get_env_missing_var_raises(self):
        with self.assertRaises(ValueError):
            get_env("MISSING_VAR")
