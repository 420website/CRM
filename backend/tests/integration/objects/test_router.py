# pyright: reportOptionalMemberAccess=none, reportArgumentType=none, reportOperatorIssue=none, reportAttributeAccessIssue=none
from io import BytesIO
import re
import pyotp
import asyncio
from unittest import IsolatedAsyncioTestCase
from datetime import date
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Response, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from app.authentication.services import UserService
from app.database import minio_client, database
from app.dependencies import get_current_user, get_user_pending_mfa
from app.objects.schemas import AttachmentCreate
from app.registration.router import create_patient
from app.registration.schemas import PatientCreate
from app.objects.services import AttachmentService, ObjectService, PhotoService
from app.registration.services import PatientService
from app.authentication.router import (
    login,
    register,
    setup_authenticator_mfa,
    verify_authenticator_mfa,
    verify_email,
)
from app.objects.router import (
    delete_attachment,
    delete_photo,
    get_attachment,
    get_photo,
    list_attachment_objects,
    upload_attachment,
    upload_photo,
)
from app.authentication.schemas import (
    LoginRequest,
    MFAVerifiactionCode,
    RegisterRequest,
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


###############
# Photos
###############
email = "test497@example.com"
password = "securepassword123"


class TestPatientPhotosRouter(IsolatedAsyncioTestCase):
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

    @classmethod
    async def asyncSetUpClass(cls):
        await database.connect()

        # Delete any user that may exist
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

    async def mock_create_patient(self, name: str):
        """Helper to create a test patient using class user"""
        patient_data = PatientCreate(
            first_name=name,
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

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_photo(self, patient_id):
        """Helper to create an attachment for a patient"""
        data = read_file(self.object_path)
        file = UploadFile(filename="test-img.jpeg", file=BytesIO(data))

        await upload_photo(patient_id, "test-img.jpeg", file, self.user)

        # Get the created photo to return its ID
        photo = await PhotoService.get_photo(patient_id)
        return photo.id if photo else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.object_path = "tests/integration/objects/docs/test-img.jpeg"
        self.file_name = "test-img.jpeg"
        self.patient_data = PatientCreate(
            first_name="Jim",
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

        self.patient_id = await self.mock_create_patient("Jim")

    async def asyncTearDown(self):
        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    #### Tests
    async def test_upload_photo_success(self):
        # load file
        file_name = "test-img.jpeg"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))

        # test
        result = await upload_photo(
            self.patient_id, file_name, file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")

        # cleanup
        key = f"{self.patient_id}/{file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_update_photo_same_name(self):
        file_name = "test-img.jpeg"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        result = await upload_photo(
            self.patient_id, file_name, file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")
        old_photo = await PhotoService.get_photo(self.patient_id)

        # test
        file_name = "test-img.jpeg"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        result = await upload_photo(
            self.patient_id, file_name, file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")
        new_photo = await PhotoService.get_photo(self.patient_id)

        self.assertEqual(old_photo.id, new_photo.id)
        self.assertEqual(old_photo.patient_id, new_photo.patient_id)
        self.assertEqual(old_photo.photo_key, new_photo.photo_key)
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

        # cleanup
        key = f"{self.patient_id}/{file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_update_photo_different_name(self):
        file_name = "test-img.jpeg"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        result = await upload_photo(
            self.patient_id, file_name, file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")
        old_photo = await PhotoService.get_photo(self.patient_id)

        # test
        file_name = "test-img2.jpeg"
        data = read_file(self.object_path)
        file = UploadFile(filename=file_name, file=BytesIO(data))
        result = await upload_photo(
            self.patient_id, file_name, file, self.user
        )
        self.assertEqual(result["message"], "Successfully uploaded file.")
        new_photo = await PhotoService.get_photo(self.patient_id)

        self.assertEqual(old_photo.id, new_photo.id)
        self.assertEqual(old_photo.patient_id, new_photo.patient_id)
        self.assertNotEqual(old_photo.photo_key, new_photo.photo_key)
        self.assertGreaterEqual(new_photo.uploaded_at, old_photo.uploaded_at)

        # cleanup
        key = f"{self.patient_id}/{file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_get_photo_base64_success(self):
        await self.mock_create_photo(self.patient_id)

        # test
        file_name = "test-img.jpeg"
        result = await get_photo(self.patient_id, "base64", self.user)
        assert result

        # Get the body content
        self.assertEqual(result["type"], "JPEG")  # pyright: ignore
        self.assertEqual(result["name"], file_name)  # pyright: ignore
        self.assertTrue(len(result["file"]) > 0)  # pyright: ignore

        # Cleanup
        key = f"{self.patient_id}/{file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_get_photo_raw_success(self):
        await self.mock_create_photo(self.patient_id)

        # test
        file_name = "test-img.jpeg"
        result = await get_photo(self.patient_id, "raw", self.user)

        # Check status code
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.media_type, "application/octet-stream")

        # Get the body content
        body = result.body
        self.assertIsInstance(body, bytes)
        self.assertGreater(len(body), 0)  # Ensure it has content
        self.assertEqual(read_file(self.object_path), body)

        # Cleanup
        key = f"{self.patient_id}/{file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_get_photo_not_fount(self):
        with self.assertRaises(HTTPException) as e:
            await get_photo(self.patient_id, "raw", self.user)

        self.assertEqual(e.exception.status_code, 404)
        self.assertEqual(
            e.exception.detail, "Photo key not found for patient."
        )

    async def test_get_photo_invalid_version(self):
        await self.mock_create_photo(self.patient_id)

        # test
        with self.assertRaises(HTTPException) as e:
            await get_photo(self.patient_id, "invalid", self.user)

        self.assertEqual(e.exception.status_code, 400)
        self.assertEqual(e.exception.detail, "Invalid version.")

        # Cleanup
        key = f"{self.patient_id}/{self.file_name}"
        await ObjectService.delete_object("photos", key)

    async def test_delete_photo_success(self):
        photo_id = await self.mock_create_photo(self.patient_id)
        self.assertIsNotNone(photo_id)

        # test
        result = await delete_photo(self.patient_id, self.user)
        self.assertEqual(result["message"], "Successfully deleted photo.")


###############
# Attachments
###############
email = "test497@example.com"
password = "securepassword123"


class TestPatientAttachmentsRouter(IsolatedAsyncioTestCase):
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

    @classmethod
    async def asyncSetUpClass(cls):
        await database.connect()

        # Clear out old users
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

    async def mock_create_patient(self, name: str):
        """Helper to create a test patient using class user"""
        patient_data = PatientCreate(
            first_name=name,
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="0000000000",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        result = await create_patient(patient_data, self.user)
        return result["patient_id"]

    async def mock_create_attachment(self, patient_id):
        """Helper to create an attachment for a patient"""
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))

        await upload_attachment(
            patient_id,
            file=file,
            file_name=self.file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            user=self.user,
        )

        # Get the created attachment to return its ID
        attachments = await AttachmentService.get_patient_attachments(
            patient_id
        )
        return attachments[0].id if attachments else None

    async def asyncSetUp(self) -> None:
        await database.connect()
        await minio_client.connect()
        asyncio.get_event_loop().set_debug(False)

        self.file_name = "test-pdf.pdf"
        self.object_path = "tests/integration/objects/docs/test-pdf.pdf"
        self.patient_data = PatientCreate(
            first_name="Timothy",
            last_name="Doe",
            dob=date(1990, 1, 1),
            age=33,
            gender="Male",
            email="jim.doe@example.com",
            phone1="416-555-0123",
            status="pending",
            health_card="0000000000",
            health_card_version="AB",
            disposition="Active",
            referral_site="Toronto",
            province="Ontario",
        )

        self.patient_id = await self.mock_create_patient("Timothy")

        # Attachment test data
        self.attachment_data = AttachmentCreate(
            file_name=f"{self.file_name}",
            file_key=f"{self.patient_id}/{self.file_name}",
            file_size=1024,
            mime_type="application/pdf",
            document_type="Consultation Report",
        )

        self.key = f"{self.patient_id}/{self.file_name}"

    async def asyncTearDown(self):
        await PatientService.delete_patient_by_id(self.patient_id)
        await minio_client.disconnect()
        await database.disconnect()

    async def test_upload_attachment_success(self):
        data = read_file(self.object_path)
        file = UploadFile(filename=self.file_name, file=BytesIO(data))

        # test
        result = await upload_attachment(
            patient_id=self.patient_id,
            file=file,
            file_name=self.file_name,
            file_size=len(data),
            mime_type="application/pdf",
            document_type="Consultation Report",
            user=self.user,
        )

        self.assertEqual(
            result["message"],
            "Attachment uploaded successfully.",
        )

        # Cleanup
        await ObjectService.delete_object("attachments", self.key)

    async def test_list_attachments(self):
        id = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(id)

        # test
        result = await list_attachment_objects(self.patient_id)
        self.assertEqual(len(result), 1)

        # validate
        await ObjectService.delete_object("attachments", self.key)

    async def test_list_attachments_none(self):
        # test
        result = await list_attachment_objects(self.patient_id)
        self.assertEqual(len(result), 0)

    async def test_get_attachments_by_patient_raw_success(self):
        await self.mock_create_attachment(self.patient_id)

        # test
        result = await get_attachment(
            self.patient_id,
            self.file_name,
            "raw",
            self.user,
        )

        # Check status code
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.media_type, "application/pdf")

        # Get the body content
        body = result.body
        self.assertIsInstance(body, bytes)
        self.assertGreater(len(body), 0)  # Ensure it has content
        self.assertEqual(read_file(self.object_path), body)

        # Cleanup
        await ObjectService.delete_object("attachments", self.key)

    async def test_get_attachments_by_patient_not_found(self):
        # test
        with self.assertRaises(HTTPException) as e:
            await get_attachment(
                self.patient_id,
                self.file_name,
                "raw",
                self.user,
            )
        self.assertEqual(e.exception.status_code, 404)
        self.assertEqual(
            e.exception.detail, "Attachment not found for patient."
        )

    async def test_get_attachments_invalid_version(self):
        await self.mock_create_attachment(self.patient_id)

        # test
        with self.assertRaises(HTTPException) as e:
            await get_attachment(
                self.patient_id,
                self.file_name,
                "other",
                self.user,
            )
        self.assertEqual(e.exception.status_code, 400)
        self.assertEqual(
            e.exception.detail, "Invalid version. Must be 'raw' or 'base64'."
        )

        # clean up
        await ObjectService.delete_object("attachments", self.key)

    async def test_delete_attachment_success(self):
        id = await self.mock_create_attachment(self.patient_id)
        self.assertIsNotNone(id)

        # test
        result = await delete_attachment(self.patient_id, self.file_name)
        self.assertEqual(result["message"], "Successfully deleted attachment.")
