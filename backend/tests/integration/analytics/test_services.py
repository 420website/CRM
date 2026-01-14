# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportAttributeAccessIssue=none
from io import BytesIO
import asyncio
import re
import uuid
import pyotp
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch
from app.database import mongo_client
from fastapi import Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from app.analytics.schema import  DataSummaryResponse, LegacyData
from app.analytics.services import LegacyDataService
from app.analytics.utils import read_legacy_data_file
from app.authentication.schemas import LoginRequest, MFAVerifiactionCode, RegisterRequest
from app.authentication.services import UserService
from app.database import database, minio_client, redis_client
from app.dependencies import get_current_user, get_user_pending_mfa
from datetime import  datetime
from app.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)

def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes
    
email = "test4@example.com"
password = "securepassword123"

user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)

@patch("app.authentication.services.EmailService", new_callable=MagicMock)
async def mock_register(mock_email_service_class) -> str:
    # Prepare a mock instance to replace EmailService()
    mock_email_service = MagicMock()
    mock_email_service.recipient.return_value = mock_email_service
    mock_email_service.subject.return_value = mock_email_service

    captured_token = {}

    def mock_body(message_obj):
        # Extract token from the HTML content in message_obj.msg
        html_content = message_obj.msg

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



def read_csv(path, filename): 
    file_bytes = read_file(path)
    return UploadFile(
        filename=filename,
        file=BytesIO(file_bytes),
        # content_type="text/csv",
    )


class TestRagService(IsolatedAsyncioTestCase):
    @classmethod
    async def get_validated_user(cls):
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

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=result.access_token,
        )

        user = await get_current_user(credentials=credentials)
        return user

    async def asyncSetUp(self) -> None:
        asyncio.get_event_loop().set_debug(False)

        await minio_client.connect()
        await database.connect()
        await redis_client.connect()
        await mongo_client.connect()

        # Clear out old users
        await UserService.delete_user(email, password)
        self.user = await self.get_validated_user()
        await LegacyDataService.delete_all_legacy_data(self.user.id)

    async def asyncTearDown(self) -> None:
        await LegacyDataService.delete_all_legacy_data(self.user.id)

        await mongo_client.disconnect()
        await redis_client.disconnect()
        await minio_client.disconnect()
        await database.disconnect()

    # @skip
    async def test_upload_legacy_data(self):
        file = read_csv("tests/integration/analytics/test_data.csv","test_data.csv")
        df = await read_legacy_data_file(file)
        
        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )

        # upload
        result = await LegacyDataService.upload_legacy_data(data, self.user.id)
        self.assertTrue(result)

        db = mongo_client.get_db()
        result = await db.legacy_data.find_one({"user_id": self.user.id})
        self.assertTrue(result['records_count'], 5)

    async def test_get_legacy_data(self):
        file = read_csv("tests/integration/analytics/test_data.csv","test_data.csv")
        df = await read_legacy_data_file(file)
        
        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )
        await LegacyDataService.upload_legacy_data(data, self.user.id)

        # upload
        result = await LegacyDataService.get_legacy_data_summary(self.user.id)
        self.assertIsInstance(result, DataSummaryResponse)
        self.assertEqual(result.total_records, 5)


    async def test_insert_legacy_data(self):
        file = read_csv("tests/integration/analytics/test_data.csv","test_data.csv")
        df = await read_legacy_data_file(file)
        
        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )
        await LegacyDataService.insert_legacy_data(data)

        # upload
        result = await LegacyDataService.get_legacy_data_summary(self.user.id)
        self.assertIsInstance(result, DataSummaryResponse)
        self.assertEqual(result.total_records, 5)

    async def test_delete_legacy_data(self):
        file = read_csv("tests/integration/analytics/test_data.csv","test_data.csv")
        df = await read_legacy_data_file(file)
        
        data = LegacyData(
            user_id=self.user.id,
            upload_id=str(uuid.uuid4()),
            filename=file.filename,
            upload_date=datetime.now(),
            records_count=len(df),
            columns=list(df.columns),
            data=df.to_dict("records"),
        )
        await LegacyDataService.insert_legacy_data(data)
        
        # Test
        await LegacyDataService.delete_all_legacy_data(self.user.id)

        # check
        with self.assertRaises(Exception) as e: 
            await LegacyDataService.get_legacy_data_summary(self.user.id)

        self.assertIn("No legacy data found.", str(e.exception))

