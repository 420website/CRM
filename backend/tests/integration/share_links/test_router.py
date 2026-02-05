# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none, reportAttributeAccessIssue=none
import asyncio
from datetime import datetime, timedelta
import datetime as dt
from io import BytesIO
from unittest import IsolatedAsyncioTestCase
from datetime import date
from fastapi import HTTPException, Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from app.core.authentication.services import UserService
from app.common.storage.postgres import database
from app.common.storage.minio import minio_client
from app.common.dependencies import get_current_user, get_user_pending_mfa
import pyotp
from app.core.objects.router import upload_attachment
from app.core.objects.services import AttachmentService, ObjectService
from app.core.registration.router import create_patient
from app.core.registration.schemas import PatientCreate
from app.core.registration.services import PatientService
from app.common.config import settings
from app.testing.router import register_user
from app.core.authentication.router import (
    login,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
)
from app.core.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
)
from app.core.share_links.router import (
    AttachmentId,
    access_share_link,
    create_share_link,
    decode_jwt,
    get_share_link_metadata,
)


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        file_bytes = file.read()
        return file_bytes


email = "test978@example.com"
password = "securepassword123"

user_create = RegisterRequest(email=email, password=password)
login_request = LoginRequest(email=email, password=password)


class TestShareLinkRouter(IsolatedAsyncioTestCase):
    @classmethod
    async def get_validated_user(cls):
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

    async def mock_create_attachment(self, patient_id):
        """Helper to create an attachment for a patient"""
        file_name = "test_document.pdf"

        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        await upload_attachment(
            patient_id,
            file=file,
            file_name="test-pdf.pdf",
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            _=self.user,
        )

        # Get the created attachment to return its ID
        attachments = await AttachmentService.get_patient_attachments(
            patient_id
        )
        return attachments[0].id if attachments else None

    @classmethod
    async def asyncSetUpClass(cls):
        await database.connect()

        await UserService.delete_user(email, password)
        cls.user = await cls.get_validated_user()
        await database.disconnect()

    @classmethod
    async def asyncTearDownClass(cls):
        await database.connect()
        await UserService.delete_user(email, password)
        await database.disconnect()

    @property
    def user(self):
        return self.__class__.user

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.object_path = "tests/integration/objects/docs/test-pdf.pdf"
        self.patient_data = PatientCreate(
            first_name="Jimothy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="1234567890",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )
        result = await create_patient(self.patient_data, self.user)
        self.patient_id = result["patient_id"]

    async def asyncTearDown(self):
        key = f"{self.patient_id}/test-pdf.pdf"
        await ObjectService.delete_object("attachments", key)
        await PatientService.delete_patient_by_id(self.patient_id)
        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    # create patient
    async def test_share_link_success(self):
        """Helper to create an attachment for a patient"""
        id = await self.mock_create_attachment(self.patient_id)

        # test
        result = await create_share_link(AttachmentId(attachment_id=id))
        token = result["share_url"].split("?")[1]
        token = token.split("=")[1]
        decode_token = decode_jwt(token)
        assert decode_token

        # validate
        # self.assertEqual(decode_token["attachment_id"], attachment_id)
        self.assertGreater(
            decode_token["exp"],
            datetime.now(dt.timezone.utc).timestamp(),
        )
        self.assertLess(
            decode_token["iat"],
            datetime.now(dt.timezone.utc).timestamp(),
        )

    async def test_share_link_no_attachment(self):
        """Helper to create an attachment for a patient"""
        attachment_id = 109876

        # test
        with self.assertRaises(HTTPException) as cm:
            await create_share_link(AttachmentId(attachment_id=attachment_id))

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.detail, "Attachment not found.")

    async def test_access_share_link_metadata_successful(self):
        """Helper to create an attachment for a patient"""
        id = await self.mock_create_attachment(self.patient_id)

        result = await create_share_link(AttachmentId(attachment_id=id))
        token = result["share_url"].split("?")[1]
        token = token.split("=")[1]

        # test
        response = await get_share_link_metadata(token)

        # validate
        self.assertEqual("test-pdf.pdf", response["file_name"])
        self.assertEqual("application/pdf", response["mime_type"])

    async def test_access_share_link_successful(self):
        """Helper to create an attachment for a patient"""
        id = await self.mock_create_attachment(self.patient_id)

        result = await create_share_link(AttachmentId(attachment_id=id))
        token = result["share_url"].split("?")[1]
        token = token.split("=")[1]

        # test
        result = await access_share_link(token)

        # Check status code
        self.assertEqual(result.status_code, 200)

        # Get the body content
        body = result.body
        self.assertIsInstance(body, bytes)
        self.assertGreater(len(body), 0)  # Ensure it has content
        self.assertEqual(read_file(self.object_path), body)

    async def test_access_share_link_invalid_jwt(self):
        expiry = datetime.now(dt.timezone.utc) - timedelta(minutes=5)
        payload = {
            "attachment_id": 1,
            "exp": int(expiry.timestamp()),
            "iat": int(datetime.now(dt.timezone.utc).timestamp()),
        }

        token = jwt.encode(
            payload,
            settings.jwt_access_secret,
            algorithm=settings.jwt_algorithm,
        )

        with self.assertRaises(HTTPException) as cm:
            await access_share_link(token)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, "Url has expired.")
